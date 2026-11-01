import datetime
from decimal import Decimal

import pytest
from django.core.management import call_command

from catalog.models import Game
from geography.models import Country
from ingestion.http import ApiError
from ingestion.management.commands import import_steam_store
from ingestion.models import ImportRun
from ingestion.sources.steam_store import SteamStoreClient
from ingestion.sources.steam_store.store_record import requirements_text
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

STARDEW = 413150
DETAILS = "steam_store/appdetails_413150_en"
RATES = "frankfurter_latest_eur"


def price_payload(currency: str, final: int, discount: int = 0) -> dict:
    overview = {
        "currency": currency,
        "initial": final,
        "final": final,
        "discount_percent": discount,
    }
    return {str(STARDEW): {"success": True, "data": {"price_overview": overview}}}


@pytest.fixture
def stardew(db: None) -> Game:
    return Game.objects.create(appid=STARDEW, name=str(STARDEW), owners_mid=35_000_000)


def use_fake_store(monkeypatch: pytest.MonkeyPatch, *responses: object) -> FakeFetcher:
    fetcher = FakeFetcher(list(responses))
    monkeypatch.setattr(
        import_steam_store, "build_client", lambda: SteamStoreClient(fetch_json=fetcher)
    )
    converter = EuroConverter.from_frankfurter(FakeFetcher([load_fixture(RATES)]))
    monkeypatch.setattr(import_steam_store, "build_converter", lambda: converter)
    return fetcher


@pytest.mark.usefixtures("stardew")
def test_imports_the_sheet_and_prices_in_euros(monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = use_fake_store(
        monkeypatch,
        load_fixture(DETAILS),
        price_payload("EUR", 1399),
        price_payload("USD", 1499, discount=50),
    )

    call_command("import_steam_store", countries="fr,us")

    game = Game.objects.get()
    assert game.name == "Stardew Valley"
    assert game.release_date == datetime.date(2016, 2, 26)
    assert "farm" in game.short_description.lower()
    assert len(game.screenshots) == 2
    assert game.store_fetched_at is not None
    assert sorted(game.genres.values_list("name", flat=True)) == ["Indie", "RPG", "Simulation"]
    assert game.developers.get().name == "ConcernedApe"
    assert "Windows" in game.platforms.values_list("name", flat=True)
    usa = PricePoint.objects.get(country="US")
    assert (usa.currency, usa.price, usa.discount_percent) == ("USD", Decimal("14.99"), 50)
    assert usa.price_eur == Decimal("13.38")
    assert PricePoint.objects.get(country="FR").price_eur == Decimal("13.99")
    assert Country.objects.get(iso2="US").iso3 == "USA"
    assert [call.get("cc") for call in fetcher.calls] == ["fr", "fr", "us"]


@pytest.mark.usefixtures("stardew")
def test_rerun_the_same_day_updates_prices(monkeypatch: pytest.MonkeyPatch) -> None:
    for final in (1499, 999):
        use_fake_store(monkeypatch, price_payload("USD", final))
        call_command("import_steam_store", countries="us", details=0)

    assert PricePoint.objects.get().price == Decimal("9.99")


@pytest.mark.usefixtures("stardew")
def test_unknown_currency_keeps_the_price_without_euros(monkeypatch: pytest.MonkeyPatch) -> None:
    use_fake_store(monkeypatch, price_payload("ARS", 1_250_000))

    call_command("import_steam_store", countries="ar", details=0)

    point = PricePoint.objects.get()
    assert point.price == Decimal("12500.00")
    assert point.price_eur is None


@pytest.mark.usefixtures("stardew")
def test_failures_are_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    failure = ApiError("steam_store", "url", "HTTP 429 après 5 essais", 429)
    use_fake_store(monkeypatch, failure, failure)

    call_command("import_steam_store", countries="fr,xx")

    errors = ImportRun.objects.get(source="steam_store").errors
    assert "HTTP 429" in errors
    assert "Pays xx" in errors


def test_requirements_become_plain_text() -> None:
    html = "<strong>Minimum:</strong><br><ul><li>OS: Windows 10</li><li>RAM&nbsp;: 2 GB</li></ul>"

    assert requirements_text(html) == "Minimum:\nOS: Windows 10\nRAM\xa0: 2 GB"
