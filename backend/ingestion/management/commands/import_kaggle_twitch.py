from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from ingestion.import_tracking import tracked_import
from ingestion.sources.kaggle.games_import import resolve_dataset_file
from ingestion.sources.kaggle.twitch_history import DATASET, FILENAME, read_history
from ingestion.sources.twitch.steam_match import appids_by_name
from players.models import TwitchMonth

SOURCE = "kaggle_twitch"


class Command(BaseCommand):
    help = (
        f"Importe le dataset Kaggle {DATASET} : le top 200 des jeux regardés sur Twitch chaque "
        "mois depuis 2016. Remplace l'historique déjà importé."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--file", type=Path, help=f"{FILENAME} déjà téléchargé à la main")
        parser.add_argument("--limit", type=int, help="ne lit que les N premières lignes")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            path = resolve_dataset_file(report, DATASET, FILENAME, options["file"])
            if path is None:
                return
            rows = read_history(path, options["limit"])
            appids = appids_by_name({row.name for row in rows})
            with transaction.atomic():
                TwitchMonth.objects.all().delete()
                TwitchMonth.objects.bulk_create(
                    TwitchMonth(
                        name=row.name, month=row.month, rank=row.rank,
                        hours_watched=row.hours_watched, avg_viewers=row.avg_viewers,
                        peak_viewers=row.peak_viewers, streamers=row.streamers,
                        game_id=appids.get(row.name),
                    )
                    for row in rows
                )  # fmt: skip
            report.rows = len(rows)
        self.stdout.write(f"Kaggle Twitch : {report.rows} lignes.")
