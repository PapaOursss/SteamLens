from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from catalog.models import Game
from geography.country_table import ensure_countries
from ingestion.api_keys import get_api_keys
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.itad import DEFAULT_COUNTRY, ItadClient
from ingestion.sources.top_games import most_owned_appids
from pricing.models import PriceChange

SOURCE = "isthereanydeal"
DEFAULT_LIMIT = 200


def build_client(api_key: str) -> ItadClient:
    return ItadClient(api_key)


class Command(BaseCommand):
    help = "Historique des prix Steam (IsThereAnyDeal) des jeux les plus possédés (T-18)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        keys = get_api_keys(SOURCE, "ITAD_API_KEY")
        if keys is None:
            return
        client = build_client(keys["ITAD_API_KEY"])
        ensure_countries({DEFAULT_COUNTRY})
        with tracked_import(SOURCE) as report:
            games = Game.objects.filter(appid__in=most_owned_appids(options["limit"]))
            for game in games:
                try:
                    report.rows += import_history(client, game)
                except ApiError as error:
                    report.add_error(str(error))
        self.stdout.write(f"IsThereAnyDeal : {report.rows} changements de prix enregistrés.")


def import_history(client: ItadClient, game: Game) -> int:
    if not game.itad_id:
        game.itad_id = client.game_id(game.appid) or ""
        game.save(update_fields=["itad_id"])
    if not game.itad_id:
        return 0
    changes = [
        PriceChange(
            game=game,
            country_id=DEFAULT_COUNTRY,
            changed_at=change.changed_at,
            currency=change.currency,
            price=change.price,
            regular=change.regular,
            cut=change.cut,
        )
        for change in client.steam_history(game.itad_id)
    ]
    PriceChange.objects.bulk_create(
        changes,
        update_conflicts=True,
        unique_fields=["game", "country", "changed_at"],
        update_fields=["currency", "price", "regular", "cut"],
    )
    return len(changes)
