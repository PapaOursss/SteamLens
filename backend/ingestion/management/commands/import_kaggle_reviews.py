from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import ReviewExcerpt
from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle.games_import import resolve_dataset_file
from ingestion.sources.kaggle.steam_reviews import (
    DATA_DATE,
    DATASET,
    FILENAME,
    LANGUAGE,
    read_excerpts,
    read_review_totals,
)
from ingestion.writing import GameRecord, GameWriter

SOURCE = "kaggle_reviews"
DEFAULT_EXCERPTS = 20


class Command(BaseCommand):
    help = (
        f"Importe le dataset Kaggle {DATASET} (6,4 M d'avis) : avis positifs / négatifs par jeu "
        "et un échantillon de textes anonymes pour les nuages de mots."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")
        parser.add_argument(
            "--excerpts", type=int, default=DEFAULT_EXCERPTS, help="extraits par jeu et par avis"
        )

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            path = resolve_dataset_file(report, DATASET, FILENAME, options["file"])
            if path is None:
                return
            totals = read_review_totals(path, options["limit"])
            records = (
                GameRecord(
                    appid=game.appid, name=game.name,
                    positive_reviews=game.positive, negative_reviews=game.negative,
                )
                for game in totals
            )  # fmt: skip
            report.rows = GameWriter(DATA_DATE, review_language=LANGUAGE).save(records)
            excerpts = read_excerpts(path, options["excerpts"], options["limit"])
            with transaction.atomic():
                ReviewExcerpt.objects.filter(source=SOURCE).delete()
                ReviewExcerpt.objects.bulk_create(
                    ReviewExcerpt(
                        game_id=excerpt.appid, text=excerpt.text,
                        is_positive=excerpt.is_positive, language=LANGUAGE, source=SOURCE,
                    )
                    for excerpt in excerpts
                )  # fmt: skip
            report.rows += len(excerpts)
        self.stdout.write(f"Kaggle Steam Reviews : {report.rows} lignes.")
