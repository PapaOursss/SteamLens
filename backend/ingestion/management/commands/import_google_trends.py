import logging
from argparse import ArgumentParser
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Game
from geography.country_table import COUNTRIES
from ingestion.http import ApiError
from ingestion.import_tracking import ImportReport, tracked_import
from ingestion.sources.google_trends import (
    GoogleTrendsClient,
    parse_trends_csv,
    save_trends_records,
)
from ingestion.sources.top_games import most_owned_appids

logger = logging.getLogger(__name__)
DEFAULT_TOP_LIMIT = 50


class Command(BaseCommand):
    help = (
        "Importe l'intérêt régional Google Trends pour les top jeux Steam "
        "(via API avec repli tolérant ou via fichier CSV)."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_TOP_LIMIT,
            help="Nombre de jeux à importer parmi les plus possédés (défaut : 50)",
        )
        parser.add_argument(
            "--csv",
            type=str,
            help="Chemin vers un export CSV Google Trends à importer pour un jeu",
        )
        parser.add_argument(
            "--appid",
            type=int,
            help="AppID cible si import par CSV",
        )
        parser.add_argument(
            "--date",
            type=str,
            help="Date du snapshot (YYYY-MM-DD), par défaut aujourd'hui",
        )

    def handle(self, *args: object, **options: object) -> None:
        snapshot_date = (
            date.fromisoformat(options["date"]) if options.get("date") else timezone.localdate()
        )
        csv_path = options.get("csv")
        appid = options.get("appid")
        limit = options.get("limit") or DEFAULT_TOP_LIMIT

        with tracked_import("google_trends") as report:
            if csv_path:
                self._import_from_csv(report, csv_path, appid, snapshot_date)
            else:
                self._import_from_api(report, limit, snapshot_date)

        self.stdout.write(f"Google Trends : {report.rows} enregistrés, {len(report.errors)} erreurs.")

    def _import_from_csv(
        self, report: ImportReport, csv_path: str, appid: int | None, snapshot_date: date
    ) -> None:
        if not appid:
            report.add_error("L'option --appid est obligatoire avec --csv.")
            return

        path = Path(csv_path)
        if not path.is_file():
            report.add_error(f"Fichier CSV introuvable : {csv_path}")
            return

        country_name_map = {row.name_fr: row.iso2 for row in COUNTRIES}
        content = path.read_text(encoding="utf-8")
        records = parse_trends_csv(content, appid, snapshot_date, country_name_map)
        saved = save_trends_records(records)
        report.rows += saved
        self.stdout.write(f"  CSV importé : {saved} pays pour appid {appid}.")

    def _import_from_api(self, report: ImportReport, limit: int, snapshot_date: date) -> None:
        appids = most_owned_appids(limit)
        client = GoogleTrendsClient()
        games = {g.appid: g for g in Game.objects.filter(appid__in=appids)}

        for aid in appids:
            game = games.get(aid)
            if not game:
                continue
            try:
                records = client.interest_by_region(game.name, aid, snapshot_date)
                saved = save_trends_records(records)
                report.rows += saved
                self.stdout.write(f"  {game.name} ({aid}) : {saved} pays.")
            except (ApiError, OSError, ValueError, KeyError) as error:
                report.add_error(f"Erreur trends pour {game.name} ({aid}) : {error}")
