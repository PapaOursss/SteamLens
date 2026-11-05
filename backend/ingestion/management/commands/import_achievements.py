from argparse import ArgumentParser
from datetime import UTC, date, datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import AchievementStat
from catalog.models.achievement_stat import PERCENT_DECIMALS
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_web_api import AchievementClient
from ingestion.sources.top_games import most_owned_appids

SOURCE = "steam_achievements"
DEFAULT_LIMIT = 300


def build_client() -> AchievementClient:
    return AchievementClient(api_key=settings.API_KEYS["STEAM_API_KEY"])


def today() -> date:
    return datetime.now(UTC).date()


class Command(BaseCommand):
    help = "Pourcentage de joueurs de chaque succès, pour les jeux les plus possédés (T-35)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        client = build_client()
        with tracked_import(SOURCE) as report:
            for appid in most_owned_appids(options["limit"]):
                try:
                    report.rows += save_achievements(appid, client, today())
                except ApiError as error:
                    report.add_error(str(error))
        self.stdout.write(f"Succès : {report.rows} lignes écrites.")


def save_achievements(appid: int, client: AchievementClient, day: date) -> int:
    rows = [
        AchievementStat(
            game_id=appid,
            name=achievement.name,
            display_name=achievement.display_name,
            description=achievement.description,
            percent=round(achievement.percent, PERCENT_DECIMALS),
            date=day,
        )
        for achievement in client.achievements(appid)
    ]
    AchievementStat.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["game", "name"],
        update_fields=["display_name", "description", "percent", "date"],
    )
    return len(rows)
