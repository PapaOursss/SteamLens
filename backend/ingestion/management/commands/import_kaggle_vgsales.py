from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from geography.models import RegionalSales
from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle.games_import import resolve_dataset_file
from ingestion.sources.kaggle.vgsales import DATASET, FILENAME, read_sales

SOURCE = "kaggle_vgsales"


class Command(BaseCommand):
    help = (
        f"Importe le dataset Kaggle {DATASET} : ventes par jeu en Amérique du Nord, en Europe, "
        "au Japon et dans le reste du monde. Remplace les ventes déjà importées."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            path = resolve_dataset_file(report, DATASET, FILENAME, options["file"])
            if path is None:
                return
            sales = read_sales(path, options["limit"])
            with transaction.atomic():
                RegionalSales.objects.all().delete()
                RegionalSales.objects.bulk_create(
                    RegionalSales(
                        name=game.name, platform=game.platform, year=game.year,
                        genre=game.genre, publisher=game.publisher, na_sales=game.na,
                        eu_sales=game.eu, jp_sales=game.jp, other_sales=game.other,
                    )
                    for game in sales
                )  # fmt: skip
            report.rows = len(sales)
        self.stdout.write(f"Kaggle vgsales : {report.rows} lignes.")
