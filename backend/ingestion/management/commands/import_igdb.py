from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from ingestion.api_keys import get_api_keys
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.igdb import IgdbClient, build_igdb_client
from ingestion.sources.igdb.igdb_writer import save_igdb_games, save_popularity
from ingestion.sources.top_games import most_owned_appids

SOURCE = "igdb"
DEFAULT_LIMIT = 2000


def build_client() -> IgdbClient | None:
    keys = get_api_keys(SOURCE, "TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET")
    if keys is None:
        return None
    return build_igdb_client(keys["TWITCH_CLIENT_ID"], keys["TWITCH_CLIENT_SECRET"])


class Command(BaseCommand):
    help = (
        "Importe IGDB pour les jeux les plus possédés : genres fins, thèmes, modes, points de "
        "vue, studios et leurs pays, PopScore. Demande l'application Twitch dans backend/.env."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            client = build_client()
            if client is None:
                report.add_error("TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET absents de backend/.env.")
                return
            try:
                links = client.steam_links(most_owned_appids(options["limit"]))
                igdb_ids = sorted(set(links.values()))
                report.rows = save_igdb_games(links, client.games(igdb_ids))
                report.rows += save_popularity(
                    links, client.popularity_types(), client.popularity(igdb_ids)
                )
            except ApiError as error:
                report.add_error(str(error))
        self.stdout.write(f"IGDB : {report.rows} lignes, {len(report.errors)} erreur(s).")
