from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.models import Game
from ingestion.import_tracking import tracked_import
from ingestion.sources.steamcharts.csv_history_parser import parse_player_history_csv
from players.models import PlayerCountSnapshot

SOURCE = "steamcharts_monthly_csv"


class Command(BaseCommand):
    help = "Importe un CSV d'historique mensuel de joueurs SteamCharts / Kaggle depuis ~2012."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("file", type=Path, help="Chemin vers le fichier CSV")
        parser.add_argument("--limit", type=int, help="Nombre maximal de lignes à lire")

    def handle(self, *args: object, **options: object) -> None:
        file_path: Path = options["file"]
        limit: int | None = options.get("limit")

        if not file_path.is_file():
            self.stderr.write(f"Fichier introuvable : {file_path}")
            return

        with tracked_import(SOURCE) as report:
            records = parse_player_history_csv(file_path, limit)
            # Garantir l'existence des jeux
            unique_games = {r.appid: r.name for r in records}
            existing_appids = set(Game.objects.filter(appid__in=unique_games.keys()).values_list("appid", flat=True))
            missing_games = [
                Game(appid=aid, name=name)
                for aid, name in unique_games.items()
                if aid not in existing_appids
            ]
            if missing_games:
                Game.objects.bulk_create(missing_games, ignore_conflicts=True)

            snapshots = [
                PlayerCountSnapshot(
                    game_id=rec.appid,
                    taken_at=rec.month_date,
                    players=rec.peak_players,
                    source=SOURCE,
                )
                for rec in records
            ]
            PlayerCountSnapshot.objects.bulk_create(
                snapshots,
                update_conflicts=True,
                unique_fields=["game", "taken_at", "source"],
                update_fields=["players"],
                batch_size=1000,
            )
            report.rows = len(snapshots)

        self.stdout.write(f"Historique mensuel : {report.rows} points importés.")
