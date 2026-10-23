import datetime
from decimal import Decimal

import pytest

from catalog.models import Company, Game, GameTag, Genre, Tag
from geography.models import Country
from players.models import PlayerCountSnapshot
from pricing.models import PricePoint

COUNTER_STRIKE_APPID = 730
DOTA_APPID = 570
STARDEW_APPID = 413150


@pytest.fixture
def catalog_sample(db: None) -> dict[str, Game]:
    """Trois jeux, deux genres, deux tags, deux pays : de quoi tester chaque endpoint."""
    action = Genre.objects.create(name="Action")
    simulation = Genre.objects.create(name="Simulation")
    shooter = Tag.objects.create(name="FPS")
    cozy = Tag.objects.create(name="Cozy")
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France", continent="Europe")
    usa = Country.objects.create(iso2="US", iso3="USA", name_fr="États-Unis")

    counter_strike = Game.objects.create(appid=COUNTER_STRIKE_APPID, name="Counter-Strike 2")
    dota = Game.objects.create(appid=DOTA_APPID, name="Dota 2", is_free=True)
    stardew = Game.objects.create(
        appid=STARDEW_APPID, name="Stardew Valley", release_date=datetime.date(2016, 2, 26)
    )
    counter_strike.genres.add(action)
    dota.genres.add(action)
    stardew.genres.add(simulation)
    GameTag.objects.create(game=counter_strike, tag=shooter, votes=900)
    GameTag.objects.create(game=stardew, tag=cozy, votes=300)

    valve = Company.objects.create(name="Valve", country=usa)
    Company.objects.create(name="Ubisoft", country=france)
    counter_strike.developers.add(valve)

    _add_prices(stardew, france, usa)
    _add_player_counts(counter_strike, dota)
    return {"counter_strike": counter_strike, "dota": dota, "stardew": stardew}


def _add_prices(game: Game, france: Country, usa: Country) -> None:
    day = datetime.date(2026, 10, 1)
    PricePoint.objects.create(
        game=game, country=france, currency="EUR", price=Decimal("13.99"),
        price_eur=Decimal("13.99"), date=day, source="steam_store",
    )  # fmt: skip
    PricePoint.objects.create(
        game=game, country=usa, currency="USD", price=Decimal("14.99"),
        price_eur=Decimal("12.80"), date=day, source="steam_store",
    )  # fmt: skip


def _add_player_counts(counter_strike: Game, dota: Game) -> None:
    earlier = datetime.datetime(2026, 10, 22, 12, tzinfo=datetime.UTC)
    later = earlier + datetime.timedelta(hours=1)
    PlayerCountSnapshot.objects.create(
        game=counter_strike, taken_at=earlier, players=1_000_000, source="steam_web_api"
    )
    PlayerCountSnapshot.objects.create(
        game=counter_strike, taken_at=later, players=1_200_000, source="steam_web_api"
    )
    PlayerCountSnapshot.objects.create(
        game=dota, taken_at=later, players=600_000, source="steam_web_api"
    )
