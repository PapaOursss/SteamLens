from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand

from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle.fronkongames import DATASET, FILENAME, read_fronkongames
from ingestion.sources.kaggle.games_import import import_games, resolve_dataset_file

SOURCE = "kaggle_fronkongames"


class Command(BaseCommand):
    help = (
        f"Importe le dataset Kaggle {DATASET} (~100 000 jeux récents) : propriétaires, pic de "
        "joueurs, temps de jeu, langues, Metacritic. Plus récent que T-06, il gagne sur lui."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            path = resolve_dataset_file(report, DATASET, FILENAME, options["file"])
            if path is not None:
                import_games(report, SOURCE, path, read_fronkongames, options["limit"])
        self.stdout.write(f"Kaggle fronkongames : {report.rows} lignes.")
