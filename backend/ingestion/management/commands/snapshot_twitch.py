from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.utils import timezone

from ingestion.api_keys import get_api_keys
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.twitch import HelixClient, build_helix_client, tally_streams
from ingestion.sources.twitch.helix_client import DEFAULT_STREAM_PAGES
from ingestion.sources.twitch.twitch_writer import RankedCategory, save_snapshot

SOURCE = "twitch"
DEFAULT_LIMIT = 100


def build_client() -> HelixClient | None:
    keys = get_api_keys(SOURCE, "TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET")
    if keys is None:
        return None
    return build_helix_client(keys["TWITCH_CLIENT_ID"], keys["TWITCH_CLIENT_SECRET"])


class Command(BaseCommand):
    help = (
        "Relève les catégories les plus regardées sur Twitch : spectateurs, streams et langue des "
        "streams (jamais qui stream). Demande l'application Twitch dans backend/.env."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de catégories")
        parser.add_argument(
            "--pages", type=int, default=DEFAULT_STREAM_PAGES, help="pages de streams par jeu"
        )

    def handle(self, *args: object, **options: object) -> None:
        taken_at = timezone.now().replace(minute=0, second=0, microsecond=0)
        with tracked_import(SOURCE) as report:
            client = build_client()
            if client is None:
                report.add_error("TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET absents de backend/.env.")
                return
            try:
                ranked = [
                    RankedCategory(
                        rank, game, tally_streams(client.streams(game["id"], options["pages"]))
                    )
                    for rank, game in enumerate(client.top_games(options["limit"]), start=1)
                ]
            except ApiError as error:
                report.add_error(str(error))
                return
            report.rows = save_snapshot(taken_at, ranked)
        self.stdout.write(f"Twitch : {report.rows} lignes, {len(report.errors)} erreur(s).")
