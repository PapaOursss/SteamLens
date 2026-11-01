from argparse import ArgumentParser
from datetime import UTC, date, datetime

from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone

from catalog.models import Game
from geography.country_table import ensure_countries
from ingestion.http import ApiError
from ingestion.import_tracking import ImportReport, tracked_import
from ingestion.sources.steam_store import SteamStoreClient, StorePrice, store_record
from ingestion.sources.steam_store.price_countries import PRICE_COUNTRY_CODES
from ingestion.sources.top_games import most_owned_appids
from ingestion.writing import GameWriter
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint

SOURCE = "steam_store"
DEFAULT_LIMIT = 1000
DEFAULT_DETAILS = 200


def build_client() -> SteamStoreClient:
    return SteamStoreClient()


def build_converter() -> EuroConverter:
    return EuroConverter.from_frankfurter()


class Command(BaseCommand):
    help = (
        "Importe le Steam Store : prix du top 1 000 dans ~40 pays (convertis en euros), puis "
        "les fiches détaillées des jeux jamais lus ou lus il y a le plus longtemps."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--limit", type=int, default=DEFAULT_LIMIT, help="jeux dont lire les prix"
        )
        parser.add_argument(
            "--details", type=int, default=DEFAULT_DETAILS, help="fiches à lire par passage"
        )
        parser.add_argument(
            "--countries", help="codes pays séparés par des virgules (défaut : les ~40 pays)"
        )

    def handle(self, *args: object, **options: object) -> None:
        self.client = build_client()
        countries = (
            options["countries"].lower().split(",") if options["countries"] else PRICE_COUNTRY_CODES
        )
        with tracked_import(SOURCE) as report:
            appids = most_owned_appids(options["limit"])
            if not appids:
                report.add_error("Aucun jeu classé : lancer d'abord manage.py import_steamspy.")
            self._import_details(report, appids, options["details"])
            self._import_prices(report, appids, countries)
        self.stdout.write(f"Steam Store : {report.rows} lignes, {len(report.errors)} erreur(s).")

    def _import_details(self, report: ImportReport, appids: list[int], limit: int) -> None:
        oldest_first = (
            Game.objects.filter(appid__in=appids)
            .order_by(F("store_fetched_at").asc(nulls_first=True), "-owners_mid")
            .values_list("appid", flat=True)[:limit]
        )
        fetched_at = datetime.now(UTC)
        records = []
        for appid in oldest_first:
            try:
                details = self.client.app_details(appid)
            except ApiError as error:
                report.add_error(str(error))
                continue
            if details is not None:
                records.append(store_record(details, fetched_at))
        report.rows += GameWriter(data_date=timezone.localdate()).save(records)

    def _import_prices(self, report: ImportReport, appids: list[int], countries: list[str]) -> None:
        try:
            converter = build_converter()
        except (ApiError, KeyError) as error:
            report.add_error(f"Taux de change indisponibles, prix sans euros : {error}")
            converter = EuroConverter({})
        known = ensure_countries(set(countries))
        today = timezone.localdate()
        for country in countries:
            if country.upper() not in known:
                report.add_error(f"Pays {country} absent de geography.country_table : sauté.")
                continue
            try:
                prices = self.client.prices(appids, country)
            except ApiError as error:
                report.add_error(str(error))
                continue
            PricePoint.objects.bulk_create(
                [price_point(price, converter, today) for price in prices],
                update_conflicts=True,
                unique_fields=["game", "country", "date", "source"],
                update_fields=["currency", "price", "price_eur", "discount_percent"],
            )
            report.rows += len(prices)


def price_point(price: StorePrice, converter: EuroConverter, day: date) -> PricePoint:
    return PricePoint(
        game_id=price.appid,
        country_id=price.country_code,
        currency=price.currency,
        price=price.final_amount,
        price_eur=converter.to_eur(price.final_amount, price.currency),
        discount_percent=price.discount_percent,
        date=day,
        source=SOURCE,
    )
