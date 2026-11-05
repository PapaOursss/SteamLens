from argparse import ArgumentParser
from collections import Counter
from datetime import UTC, date, datetime

from django.core.management.base import BaseCommand

from geography.country_table import ensure_countries
from geography.models import ProfileCountryCount, ProfileSample
from ingestion.api_keys import get_api_keys
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_reviews import SteamReviewsClient
from ingestion.sources.steam_web_api import NO_COUNTRY, ProfileCountryClient
from ingestion.sources.top_games import most_owned_appids

SOURCE = "steam_profiles"
DEFAULT_LIMIT = 50
DEFAULT_PAGES = 3


def build_clients(api_key: str) -> tuple[SteamReviewsClient, ProfileCountryClient]:
    return SteamReviewsClient(), ProfileCountryClient(api_key)


def today() -> date:
    return datetime.now(UTC).date()


class Command(BaseCommand):
    help = "Pays déclarés des auteurs d'avis récents (profils publics), comptés par jeu."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")
        parser.add_argument(
            "--pages", type=int, default=DEFAULT_PAGES, help="pages de 100 avis récents par jeu"
        )

    def handle(self, *args: object, **options: object) -> None:
        keys = get_api_keys(SOURCE, "STEAM_API_KEY")
        if keys is None:
            return
        reviews, profiles = build_clients(keys["STEAM_API_KEY"])
        with tracked_import(SOURCE) as report:
            for appid in most_owned_appids(options["limit"]):
                try:
                    authors = {
                        review.author_steamid
                        for review in reviews.recent_reviews(appid, max_pages=options["pages"])
                        if review.author_steamid
                    }
                    report.rows += save_sample(appid, profiles.count_countries(authors), today())
                except ApiError as error:
                    report.add_error(str(error))
        self.stdout.write(f"Pays des profils : {report.rows} lignes écrites.")


def save_sample(appid: int, countries: Counter[str], day: date) -> int:
    """Enregistre les comptes par pays et la taille de l'échantillon, rien d'autre."""
    known = ensure_countries(set(countries) - {NO_COUNTRY})
    rows = [
        ProfileCountryCount(game_id=appid, country_id=code, date=day, profiles=count)
        for code, count in countries.items()
        if code in known
    ]
    ProfileCountryCount.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["game", "country", "date"],
        update_fields=["profiles"],
    )
    ProfileSample.objects.update_or_create(
        game_id=appid,
        date=day,
        defaults={
            "profiles": countries.total(),
            "without_country": countries[NO_COUNTRY],
            "unmapped_country": sum(
                count for code, count in countries.items() if code and code not in known
            ),
        },
    )
    return len(rows) + 1
