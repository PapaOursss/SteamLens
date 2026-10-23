"""Les fixtures restent lisibles et servies sans réseau par le client des imports."""

from pathlib import Path

import pytest
import respx

from ingestion.http import ApiClient
from tests.fixture_files import FIXTURES_DIR, load_fixture

STEAMSPY_URL = "https://steamspy.com/api.php"
STEAM_STORE_URL = "https://store.steampowered.com/api/appdetails"
STARDEW_APPID = 413150


def no_wait(seconds: float) -> None:
    """`sleep` des tests : on ne fait pas vraiment attendre."""


@pytest.mark.parametrize("path", sorted(FIXTURES_DIR.glob("*.json")), ids=lambda path: path.stem)
def test_every_fixture_is_valid_json(path: Path) -> None:
    assert load_fixture(path.stem) is not None


@respx.mock
def test_steamspy_fixture_is_served_without_network() -> None:
    respx.get(STEAMSPY_URL).respond(json=load_fixture("steamspy_appdetails_413150"))
    client = ApiClient("steamspy", sleep=no_wait)

    body = client.get_json(STEAMSPY_URL, {"request": "appdetails", "appid": STARDEW_APPID})

    assert isinstance(body, dict)
    assert body["name"] == "Stardew Valley"
    assert body["owners"] == "20,000,000 .. 50,000,000"


@respx.mock
def test_steam_store_fixture_carries_the_price_in_cents() -> None:
    respx.get(STEAM_STORE_URL).respond(json=load_fixture("steam_store_price_413150_us"))
    client = ApiClient("steam_store", sleep=no_wait)

    body = client.get_json(STEAM_STORE_URL, {"appids": STARDEW_APPID, "cc": "us"})

    assert isinstance(body, dict)
    price = body[str(STARDEW_APPID)]["data"]["price_overview"]
    assert (price["currency"], price["final"]) == ("USD", 1499)
