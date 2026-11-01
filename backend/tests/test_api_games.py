from django.test import Client

from catalog.models import Game
from tests.conftest import COUNTER_STRIKE_APPID, STARDEW_APPID


def names(response_json: dict[str, list[dict[str, str]]]) -> list[str]:
    return [game["name"] for game in response_json["results"]]


def test_lists_the_games_paginated(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get("/api/games/").json()

    assert body["count"] == 3
    assert names(body) == ["Counter-Strike 2", "Dota 2", "Stardew Valley"]


def test_filters_by_search_genre_and_tag(client: Client, catalog_sample: dict[str, Game]) -> None:
    assert names(client.get("/api/games/?search=dota").json()) == ["Dota 2"]
    assert names(client.get("/api/games/?genre=action").json()) == ["Counter-Strike 2", "Dota 2"]
    assert names(client.get("/api/games/?tag=Cozy").json()) == ["Stardew Valley"]


def test_orders_by_the_requested_field(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get("/api/games/?order=-appid").json()

    assert names(body) == ["Stardew Valley", "Counter-Strike 2", "Dota 2"]


def test_game_detail_flattens_its_lists(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get(f"/api/games/{COUNTER_STRIKE_APPID}/").json()

    assert body["genres"] == ["Action"]
    assert body["tags"] == [{"name": "FPS", "votes": 900}]
    assert body["developers"] == ["Valve"]


def test_unknown_game_is_a_404(client: Client, catalog_sample: dict[str, Game]) -> None:
    assert client.get("/api/games/1/").status_code == 404


def test_player_curve_is_in_time_order(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get(f"/api/games/{COUNTER_STRIKE_APPID}/players/").json()

    assert [point["players"] for point in body] == [1_000_000, 1_200_000]


def test_prices_can_be_narrowed_to_one_country(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    every_country = client.get(f"/api/games/{STARDEW_APPID}/prices/").json()
    france_only = client.get(f"/api/games/{STARDEW_APPID}/prices/?country=fr").json()

    assert len(every_country) == 2
    assert [(price["country"], price["price"]) for price in france_only] == [("FR", "13.99")]
