from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle import KaggleDownloadError, dataset_file
from ingestion.sources.kaggle.cleaning import latest_date
from ingestion.sources.kaggle.steam_complete import DATASET, FILENAME, read_steam_complete
from ingestion.sources.kaggle.usd_price import save_usd_prices
from ingestion.writing import GameWriter
from pricing.euro_converter import EuroConverter

SOURCE = "kaggle_steam_complete"


def build_converter() -> EuroConverter:
    try:
        return EuroConverter.from_frankfurter()
    except (ApiError, KeyError):
        return EuroConverter({})


class Command(BaseCommand):
    help = f"Importe le dataset Kaggle {DATASET} (~40 000 jeux, 2019) : genres, tags, prix, avis."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            try:
                path = options["file"] or dataset_file(DATASET, FILENAME)
            except KaggleDownloadError as error:
                report.add_error(str(error))
                return
            if path is None:
                report.add_error("Clés Kaggle absentes : passer --file ou remplir backend/.env.")
                return
            games = read_steam_complete(path, options["limit"])
            data_date = latest_date(
                [game.record.fields["release_date"] for game in games], timezone.localdate()
            )
            report.rows = GameWriter(data_date).save(game.record for game in games)
            prices = [game.price for game in games if game.price is not None]
            report.rows += save_usd_prices(prices, SOURCE, data_date, build_converter())
        self.stdout.write(f"Kaggle Steam Complete : {report.rows} lignes ({path}).")
