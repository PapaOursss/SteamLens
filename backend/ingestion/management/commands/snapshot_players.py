from argparse import ArgumentParser
from datetime import UTC, datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_web_api import PlayerCountClient
from ingestion.sources.top_games import most_owned_appids
from players.models import PlayerCountSnapshot

SOURCE = "steam_web_api"
DEFAULT_LIMIT = 500


def build_client(taken_at: datetime) -> PlayerCountClient:
    return PlayerCountClient(now=lambda: taken_at, api_key=settings.API_KEYS["STEAM_API_KEY"])


def run_timestamp() -> datetime:
    """Une seule heure pour toute la photo, à la minute : les courbes restent alignées."""
    return datetime.now(UTC).replace(second=0, microsecond=0)


class Command(BaseCommand):
    help = "Photographie les joueurs connectés des jeux les plus possédés (toutes les heures)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        taken_at = run_timestamp()
        client = build_client(taken_at)
        with tracked_import("snapshot_players") as report:
            appids = most_owned_appids(options["limit"])
            if not appids:
                report.add_error("Aucun jeu classé : lancer d'abord manage.py import_steamspy.")
            snapshots = []
            for appid in appids:
                try:
                    count = client.current_players(appid)
                except ApiError as error:
                    report.add_error(str(error))
                    continue
                if count is not None:
                    snapshots.append(
                        PlayerCountSnapshot(
                            game_id=appid, taken_at=taken_at, players=count.player_count,
                            source=SOURCE,
                        )
                    )  # fmt: skip
            PlayerCountSnapshot.objects.bulk_create(
                snapshots,
                update_conflicts=True,
                unique_fields=["game", "taken_at", "source"],
                update_fields=["players"],
            )
            report.rows = len(snapshots)
        self.stdout.write(f"Joueurs connectés : {report.rows} jeux photographiés.")
