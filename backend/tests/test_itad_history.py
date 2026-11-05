import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game
from ingestion.management.commands import import_itad_history
from ingestion.sources.itad import ItadClient
from pricing.models import PriceChange
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

LOOKUP = "itad/lookup_413150"
HISTORY = "itad/history_413150_extract"
ITAD_ID = "018d937f-07a0-7290-8a3f-6c8a1f1c5d01"


def test_lookup_gives_the_itad_id() -> None:
    fetcher = FakeFetcher([load_fixture(LOOKUP), {"found": False}])
    client = ItadClient("secret", fetch_json=fetcher)
    assert client.game_id(413150) == ITAD_ID
    assert client.game_id(1) is None
    assert fetcher.calls[0] == {"key": "secret", "appid": "413150"}


def test_history_is_sorted_from_oldest() -> None:
    fetcher = FakeFetcher([load_fixture(HISTORY)])
    history = ItadClient("secret", fetch_json=fetcher).steam_history(ITAD_ID)
    assert [change.cut for change in history] == [0, 30, 0, 40]
    assert fetcher.calls[0]["shops"] == "61"


@pytest.fixture
def imported_history(db: None, monkeypatch: pytest.MonkeyPatch) -> Game:
    game = Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)
    fetcher = FakeFetcher([load_fixture(LOOKUP), load_fixture(HISTORY)])
    monkeypatch.setattr(
        import_itad_history, "build_client", lambda key: ItadClient(key, fetch_json=fetcher)
    )
    with override_settings(API_KEYS={"ITAD_API_KEY": "secret"}):
        call_command("import_itad_history", limit=1)
    return game


def test_import_links_the_game_and_stores_changes(imported_history: Game) -> None:
    imported_history.refresh_from_db()
    assert imported_history.itad_id == ITAD_ID
    assert PriceChange.objects.count() == 4


@pytest.mark.usefixtures("imported_history")
def test_price_history_summary() -> None:
    data = APIClient().get(reverse("stats-price-history", args=[413150])).json()
    summary = data["summary"]
    assert (summary["lowest_price"], summary["lowest_date"]) == (8.39, "2025-12-18")
    assert (summary["promotions"], summary["average_cut"]) == (2, 35.0)
    assert summary["by_year"] == [{"year": 2024, "promotions": 0}, {"year": 2025, "promotions": 2}]


@pytest.mark.usefixtures("imported_history")
def test_sales_calendar_counts_promo_starts_by_week() -> None:
    data = APIClient().get(reverse("stats-sales-calendar")).json()
    assert data["years"] == [2025]
    assert data["cells"] == [[2025, 26, 1], [2025, 51, 1]]


@pytest.mark.django_db
@override_settings(API_KEYS={"ITAD_API_KEY": ""})
def test_import_is_skipped_without_key() -> None:
    call_command("import_itad_history")
    assert not PriceChange.objects.exists()
