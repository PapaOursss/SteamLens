from argparse import ArgumentParser
from collections.abc import Callable

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Game
from ingestion.http import ApiError
from ingestion.import_tracking import ImportReport, tracked_import
from ingestion.sources.steamspy import SteamSpyClient, SteamSpyGame, steamspy_record
from ingestion.writing import GameWriter
from players.models import RankingEntry

DEFAULT_DETAILS = 500
DETAILS_BATCH = 100


def build_client() -> SteamSpyClient:
    return SteamSpyClient()


class Command(BaseCommand):
    help = (
        "Importe SteamSpy : catalogue (pages de 1 000 jeux, 1 par minute), top 100, puis les "
        "tags votés des jeux les plus possédés."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--pages", type=int, help="nombre de pages du catalogue (défaut : toutes)"
        )
        parser.add_argument(
            "--details", type=int, default=DEFAULT_DETAILS, help="jeux dont lire les tags votés"
        )
        parser.add_argument(
            "--skip-catalog", action="store_true", help="ne relit pas le catalogue complet"
        )

    def handle(self, *args: object, **options: object) -> None:
        self.client = build_client()
        self.today = timezone.localdate()
        self.writer = GameWriter(data_date=self.today)
        with tracked_import("steamspy") as report:
            if not options["skip_catalog"]:
                self._import_catalog(report, options["pages"])
            self._import_rankings(report)
            self._import_details(report, options["details"])
        self.stdout.write(f"SteamSpy : {report.rows} lignes, {len(report.errors)} erreur(s).")

    def _import_catalog(self, report: ImportReport, max_pages: int | None) -> None:
        page = 0
        while max_pages is None or page < max_pages:
            try:
                games = self.client.all_games_page(page)
            except ApiError as error:
                report.add_error(str(error))
                return
            if not games:
                return
            report.rows += self.writer.save(steamspy_record(game) for game in games)
            self.stdout.write(f"  page {page} : {len(games)} jeux")
            page += 1

    def _import_rankings(self, report: ImportReport) -> None:
        charts: tuple[tuple[str, Callable[[], list[SteamSpyGame]]], ...] = (
            (RankingEntry.TOP_100_IN_2_WEEKS, self.client.top_100_in_2_weeks),
            (RankingEntry.TOP_100_FOREVER, self.client.top_100_forever),
        )
        for chart, fetch in charts:
            try:
                games = fetch()
            except ApiError as error:
                report.add_error(str(error))
                continue
            report.rows += self.writer.save(steamspy_record(game) for game in games)
            RankingEntry.objects.filter(chart=chart, date=self.today).delete()
            RankingEntry.objects.bulk_create(
                RankingEntry(chart=chart, date=self.today, rank=rank, game_id=game.appid)
                for rank, game in enumerate(games, start=1)
            )

    def _import_details(self, report: ImportReport, limit: int) -> None:
        appids = list(
            Game.objects.filter(owners_mid__isnull=False)
            .order_by("-owners_mid", "-peak_ccu")
            .values_list("appid", flat=True)[:limit]
        )
        games: list[SteamSpyGame] = []
        for appid in appids:
            try:
                games.append(self.client.app_details(appid))
            except (ApiError, KeyError, ValueError) as error:
                report.add_error(f"appdetails {appid} : {error}")
            if len(games) >= DETAILS_BATCH:
                report.rows += self.writer.save(steamspy_record(game) for game in games)
                games = []
        report.rows += self.writer.save(steamspy_record(game) for game in games)
