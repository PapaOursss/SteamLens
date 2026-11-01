from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steamcharts import SteamChartsClient
from ingestion.sources.top_games import most_owned_appids
from players.models import PlayerCountSnapshot

SOURCE = "steamcharts"
DEFAULT_LIMIT = 200


def build_client() -> SteamChartsClient:
    return SteamChartsClient()


class Command(BaseCommand):
    help = (
        "Comble le passé : historique SteamCharts des joueurs connectés des jeux les plus possédés."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        client = build_client()
        with tracked_import(SOURCE) as report:
            for appid in most_owned_appids(options["limit"]):
                try:
                    history = client.history(appid)
                except ApiError as error:
                    report.add_error(str(error))
                    continue
                PlayerCountSnapshot.objects.bulk_create(
                    [
                        PlayerCountSnapshot(
                            game_id=appid, taken_at=count.counted_at,
                            players=count.player_count, source=SOURCE,
                        )
                        for count in history
                    ],
                    update_conflicts=True,
                    unique_fields=["game", "taken_at", "source"],
                    update_fields=["players"],
                )  # fmt: skip
                report.rows += len(history)
        self.stdout.write(f"SteamCharts : {report.rows} points d'historique.")
