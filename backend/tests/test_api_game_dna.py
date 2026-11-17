import datetime
from decimal import Decimal

from django.test import Client

from catalog.models import AchievementStat, Game, GamePlaytime, ReviewSummary
from players.models import TwitchStreamSnapshot
from tests.conftest import COUNTER_STRIKE_APPID, DOTA_APPID, STARDEW_APPID

DAY = datetime.date(2026, 10, 1)


def axes(client: Client, appid: int) -> dict[str, dict]:
    body = client.get(f"/api/games/{appid}/dna/").json()
    return {axis["key"]: {"score": axis["score"], "raw": axis["raw"]} for axis in body}


def _add_measures(games: dict[str, Game]) -> None:
    for name, owners, positive in (("counter_strike", 50_000_000, 80), ("stardew", 20_000_000, 98)):
        game = games[name]
        game.owners_mid = owners
        game.save()
        ReviewSummary.objects.create(
            game=game, language="all", positive=positive, negative=100 - positive, date=DAY
        )
    GamePlaytime.objects.create(game=games["stardew"], median_playtime_minutes=3000)
    GamePlaytime.objects.create(game=games["dota"], median_playtime_minutes=0)
    TwitchStreamSnapshot.objects.create(
        game=games["counter_strike"], taken_at=datetime.datetime(2026, 10, 1, tzinfo=datetime.UTC),
        viewer_count=90_000,
    )  # fmt: skip
    for name, percent in (("a", "40.00"), ("b", "10.00")):
        AchievementStat.objects.create(
            game=games["stardew"], name=name, percent=Decimal(percent), date=DAY
        )


def test_ranks_each_axis_among_measured_games(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    _add_measures(catalog_sample)

    counter_strike = axes(client, COUNTER_STRIKE_APPID)
    stardew = axes(client, STARDEW_APPID)

    assert counter_strike["popularity"] == {"score": 100, "raw": 50_000_000}
    assert stardew["popularity"]["score"] == 0
    assert stardew["rating"] == {"score": 100, "raw": 98}
    assert stardew["achievement_rarity"] == {"score": 100, "raw": 75}


def test_free_game_costs_nothing_and_missing_data_is_none(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    _add_measures(catalog_sample)

    dota = axes(client, DOTA_APPID)
    stardew = axes(client, STARDEW_APPID)

    assert dota["price"] == {"score": 0, "raw": 0}
    assert stardew["price"] == {"score": 100, "raw": 13.99}
    assert dota["lifespan"] == {"score": None, "raw": None}
    assert dota["twitch"] == {"score": None, "raw": None}
