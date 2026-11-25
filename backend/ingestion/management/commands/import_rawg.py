from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from catalog.models import Game
from ingestion.api_keys import get_api_keys
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.rawg import RawgClient, save_rawg_game_data
from ingestion.sources.top_games import most_owned_appids

SOURCE = "rawg"
DEFAULT_LIMIT = 50


class Command(BaseCommand):
    help = "Importe RAWG (notes, Metacritic, tags, temps de jeu, captures) pour les jeux les plus possédés."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Nombre de jeux à enrichir")
        parser.add_argument("--appid", type=int, help="Appid Steam unique à enrichir")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            keys = get_api_keys(SOURCE, "RAWG_API_KEY")
            if keys is None:
                report.add_error("RAWG_API_KEY absente de backend/.env.")
                return

            client = RawgClient(keys["RAWG_API_KEY"])
            appids = [options["appid"]] if options.get("appid") else most_owned_appids(options["limit"])

            games = Game.objects.filter(appid__in=appids)
            saved_count = 0
            for game in games:
                try:
                    res = client.find_game(game.appid, game.name)
                    if res is None:
                        continue
                    rawg_id = res["id"]
                    details = client.game_details(rawg_id)
                    details["screenshots"] = client.game_screenshots(rawg_id)
                    if save_rawg_game_data(game.appid, details):
                        saved_count += 1
                except ApiError as error:
                    report.add_error(f"Erreur RAWG pour {game.name} ({game.appid}) : {error}")

            report.rows = saved_count
        self.stdout.write(f"RAWG : {report.rows} jeux enrichis, {len(report.errors)} erreur(s).")
