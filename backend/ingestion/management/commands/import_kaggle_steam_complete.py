from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand

from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle.games_import import import_games, resolve_dataset_file
from ingestion.sources.kaggle.steam_complete import DATASET, FILENAME, read_steam_complete

SOURCE = "kaggle_steam_complete"


class Command(BaseCommand):
    help = f"Importe le dataset Kaggle {DATASET} (~40 000 jeux, 2019) : genres, tags, prix, avis."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            path = resolve_dataset_file(report, DATASET, FILENAME, options["file"])
            if path is not None:
                import_games(report, SOURCE, path, read_steam_complete, options["limit"])
        self.stdout.write(f"Kaggle Steam Complete : {report.rows} lignes.")
