from argparse import ArgumentParser
from datetime import UTC, date, datetime

from django.core.management.base import BaseCommand

from catalog.models import ReviewExcerpt, ReviewSummary, ReviewWeek
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_reviews import (
    RecentReview,
    SteamReviewsClient,
    count_by_week,
    pick_excerpts,
    sum_by_week,
)
from ingestion.sources.steam_reviews.steam_reviews_client import MIN_FULL_PAGE
from ingestion.sources.top_games import most_owned_appids

SOURCE = "steam_reviews"
DEFAULT_LIMIT = 200
DEFAULT_PAGES = 5
# Les langues les plus présentes dans l'enquête Steam (T-27), noms de l'API Steam.
LANGUAGES = (
    "english", "schinese", "russian", "spanish", "brazilian", "german",
    "french", "japanese", "koreana", "polish", "turkish",
)  # fmt: skip


def build_client() -> SteamReviewsClient:
    return SteamReviewsClient()


def today() -> date:
    return datetime.now(UTC).date()


class Command(BaseCommand):
    help = "Avis Steam des jeux les plus possédés : totaux par langue et ratio par semaine."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")
        parser.add_argument(
            "--pages", type=int, default=DEFAULT_PAGES, help="pages de 100 avis récents par jeu"
        )

    def handle(self, *args: object, **options: object) -> None:
        client = build_client()
        with tracked_import(SOURCE) as report:
            appids = most_owned_appids(options["limit"])
            if not appids:
                report.add_error("Aucun jeu classé : lancer d'abord manage.py import_steamspy.")
            for appid in appids:
                try:
                    report.rows += import_language_counts(client, appid, today())
                    reviews = list(client.recent_reviews(appid, max_pages=options["pages"]))
                    report.rows += import_weeks(client, appid, reviews, options["pages"])
                    report.rows += import_excerpts(appid, reviews)
                except ApiError as error:
                    report.add_error(str(error))
        self.stdout.write(f"Avis Steam : {report.rows} lignes écrites.")


def import_language_counts(client: SteamReviewsClient, appid: int, day: date) -> int:
    summaries = [
        ReviewSummary(
            game_id=appid,
            language=counts.language,
            positive=counts.positive,
            negative=counts.negative,
            date=day,
        )
        for counts in (client.counts(appid, language) for language in LANGUAGES)
        if counts is not None and counts.positive + counts.negative
    ]
    ReviewSummary.objects.bulk_create(
        summaries,
        update_conflicts=True,
        unique_fields=["game", "language", "date"],
        update_fields=["positive", "negative"],
    )
    return len(summaries)


def import_weeks(
    client: SteamReviewsClient, appid: int, reviews: list[RecentReview], pages: int
) -> int:
    weeks = count_by_week(reviews)
    if weeks and len(reviews) >= pages * MIN_FULL_PAGE:
        # Pagination coupée : la semaine la plus ancienne n'est vue qu'en partie.
        del weeks[min(weeks)]
        # Trop d'avis pour les lire un par un : l'histogramme donne les semaines manquantes.
        weeks = sum_by_week(client.daily_counts(appid)) | weeks
    rows = [
        ReviewWeek(game_id=appid, week_start=start, positive=counts.positive,
                   negative=counts.negative)
        for start, counts in weeks.items()
    ]  # fmt: skip
    ReviewWeek.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["game", "week_start"],
        update_fields=["positive", "negative"],
    )
    return len(rows)


def import_excerpts(appid: int, reviews: list[RecentReview]) -> int:
    """Remplace les extraits Steam du jeu par ceux des avis récents (nuages de mots, T-40)."""
    excerpts = [
        ReviewExcerpt(game_id=appid, text=review.text, is_positive=review.voted_up,
                      language=review.language, source=SOURCE)
        for review in pick_excerpts(reviews)
    ]  # fmt: skip
    ReviewExcerpt.objects.filter(game_id=appid, source=SOURCE).delete()
    ReviewExcerpt.objects.bulk_create(excerpts)
    return len(excerpts)
