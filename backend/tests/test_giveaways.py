import pytest
from django.test import Client

from ingestion.http import ApiError
from ingestion.sources.gamerpower import GamerPowerClient
from pricing import views_giveaways
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

URL = "/api/stats/giveaways/"


def serve(monkeypatch: pytest.MonkeyPatch, response: object) -> None:
    client = GamerPowerClient(FakeFetcher([response]))
    monkeypatch.setattr(views_giveaways, "build_client", lambda: client)


def test_active_giveaways_are_listed(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, load_fixture("gamerpower/giveaways_extract"))

    offers = client.get(URL).json()

    assert offers[0]["title"] == "Dwarven Realms (Steam) Key Giveaway"
    assert offers[0]["end_date"] is None


def test_expired_giveaways_are_hidden(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    offer = load_fixture("gamerpower/giveaways_extract")[0]
    serve(monkeypatch, [{**offer, "end_date": "2020-01-01 00:00:00"}])

    assert client.get(URL).json() == []


def test_no_giveaway_answers_an_object(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, {"status": 0, "status_message": "No active giveaways"})

    assert client.get(URL).json() == []


def test_source_down_answers_503(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    serve(monkeypatch, ApiError("gamerpower", "url", "HTTP 500"))

    assert client.get(URL).status_code == 503
