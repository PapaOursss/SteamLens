from argparse import ArgumentParser
from datetime import UTC, date, datetime

from django.core.management.base import BaseCommand

from catalog.models import ReviewSummary, ReviewWeek
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_reviews import SteamReviewsClient, count_by_week
from ingestion.sources.steam_reviews.steam_reviews_client import REVIEWS_PER_PAGE
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
                    report.rows += import_weeks(client, appid, options["pages"])
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


def import_weeks(client: SteamReviewsClient, appid: int, pages: int) -> int:
    reviews = list(client.recent_reviews(appid, max_pages=pages))
    weeks = count_by_week(reviews)
    if weeks and len(reviews) >= pages * REVIEWS_PER_PAGE:
        # Pagination coupée : la semaine la plus ancienne n'est vue qu'en partie.
        del weeks[min(weeks)]
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
