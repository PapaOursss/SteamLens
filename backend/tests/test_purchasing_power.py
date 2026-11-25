import pytest
from django.core.management import call_command
from django.test import Client

from catalog.models import Game
from geography.models import CountryIndicator
from ingestion.http import ApiError
from ingestion.management.commands import import_world_bank
from ingestion.models import ImportRun
from ingestion.sources.world_bank import WorldBankClient
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

URL = "/api/stats/purchasing-power/"


def run_import(monkeypatch: pytest.MonkeyPatch, responses: list) -> None:
    client = WorldBankClient(FakeFetcher(responses))
    monkeypatch.setattr(import_world_bank, "build_client", lambda: client)
    call_command("import_world_bank")


@pytest.fixture
def incomes(catalog_sample: dict[str, Game]) -> dict[str, Game]:
    for iso2, value in (("FR", 52_000), ("US", 104_000)):
        CountryIndicator.objects.create(
            country_id=iso2, indicator=CountryIndicator.GDP_PER_CAPITA, year=2025, value=value
        )
    return catalog_sample


def test_import_skips_aggregates_and_is_idempotent(
    db: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = load_fixture("world_bank/gdp_extract")

    run_import(monkeypatch, [body, body])
    run_import(monkeypatch, [body, body])

    gdp = CountryIndicator.objects.filter(indicator=CountryIndicator.GDP_PER_CAPITA)
    assert set(gdp.values_list("country_id", flat=True)) == {"FR", "US", "TR"}
    assert CountryIndicator.objects.count() == 6


def test_one_failed_indicator_keeps_the_other(db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    body = load_fixture("world_bank/gdp_extract")

    run_import(monkeypatch, [ApiError("world_bank", "url", "HTTP 500"), body])

    assert CountryIndicator.objects.count() == 3
    assert not ImportRun.objects.get().succeeded


def test_api_error_body_gives_no_value() -> None:
    client = WorldBankClient(FakeFetcher([[{"message": [{"id": "120"}]}]]))

    assert client.latest("nope") == []


def test_hours_at_local_and_american_prices(client: Client, incomes: dict[str, Game]) -> None:
    body = client.get(URL, {"appid": incomes["stardew"].appid}).json()

    rows = {row["iso3"]: row for row in body["countries"]}
    assert rows["FRA"]["hours"] == pytest.approx(13.99 * 2080 / 52_000, abs=0.01)
    assert rows["FRA"]["hours_uniform"] == pytest.approx(12.80 * 2080 / 52_000, abs=0.01)
    assert body["has_local_prices"] is True


def test_without_game_everyone_pays_sixty_euros(client: Client, incomes: dict[str, Game]) -> None:
    body = client.get(URL).json()

    assert body["uniform_price_eur"] == 60
    assert body["countries"][0]["iso3"] == "FRA"
    assert body["countries"][0]["hours"] is None
    assert body["countries"][0]["hours_uniform"] == 2.4


def test_bad_appid(client: Client, db: None) -> None:
    assert client.get(URL, {"appid": "abc"}).status_code == 400
    assert client.get(URL, {"appid": "1"}).status_code == 404
