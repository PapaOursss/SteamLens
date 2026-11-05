import datetime
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game
from geography.models import Country
from ingestion.http import ApiError
from ingestion.management.commands import import_itad_history
from ingestion.models import ImportRun
from ingestion.sources.itad import ItadClient
from pricing.models import PriceChange
from pricing.price_history import history_summary, promo_starts
from tests.fake_fetcher import FakeFetcher

ITAD_ID = "018d937f-0000"
UTC = datetime.UTC


def deal(timestamp: str, price: float, regular: float, cut: int | None) -> dict:
    row = {"timestamp": timestamp, "shop": {"id": 61, "name": "Steam"},
           "deal": {"price": {"amount": price, "currency": "EUR"},
                    "regular": {"amount": regular, "currency": "EUR"}}}  # fmt: skip
    if cut is not None:
        row["deal"]["cut"] = cut
    return row


def test_lookup_without_game_gives_none() -> None:
    assert ItadClient("k", fetch_json=FakeFetcher([{"found": True}])).game_id(1) is None


def test_lookup_of_a_non_object_gives_none() -> None:
    assert ItadClient("k", fetch_json=FakeFetcher([[]])).game_id(1) is None


def test_history_without_deal_rows_is_skipped() -> None:
    rows = [{"timestamp": "2025-01-01T00:00:00+00:00", "deal": None},
            deal("2025-02-01T00:00:00+00:00", 5, 10, 50)]  # fmt: skip
    history = ItadClient("k", fetch_json=FakeFetcher([rows])).steam_history(ITAD_ID)
    assert [change.cut for change in history] == [50]


def test_a_missing_cut_means_full_price() -> None:
    rows = [deal("2025-02-01T00:00:00+00:00", 10, 10, None)]
    assert ItadClient("k", fetch_json=FakeFetcher([rows])).steam_history(ITAD_ID)[0].cut == 0


def test_prices_are_exact_decimals() -> None:
    rows = [deal("2025-02-01T00:00:00+00:00", 8.39, 13.99, 40)]
    change = ItadClient("k", fetch_json=FakeFetcher([rows])).steam_history(ITAD_ID)[0]
    assert (change.price, change.regular) == (Decimal("8.39"), Decimal("13.99"))


def test_timestamps_keep_their_offset() -> None:
    rows = [deal("2025-06-26T19:03:02+02:00", 1, 1, 0)]
    change = ItadClient("k", fetch_json=FakeFetcher([rows])).steam_history(ITAD_ID)[0]
    assert change.changed_at == datetime.datetime(2025, 6, 26, 17, 3, 2, tzinfo=UTC)


def test_history_request_targets_steam_in_france() -> None:
    fetcher = FakeFetcher([[]])
    ItadClient("k", fetch_json=fetcher).steam_history(ITAD_ID)
    assert fetcher.calls == [{"key": "k", "id": ITAD_ID, "country": "FR", "shops": "61"}]


def changes(*cuts: int) -> list[PriceChange]:
    start = datetime.datetime(2025, 1, 6, tzinfo=UTC)
    return [PriceChange(changed_at=start + datetime.timedelta(weeks=index), price=Decimal(10 - cut / 10),
                        regular=Decimal(10), cut=cut, currency="EUR")
            for index, cut in enumerate(cuts)]  # fmt: skip


def test_no_change_no_promo() -> None:
    assert promo_starts([]) == []


def test_a_history_starting_in_promo_counts_it() -> None:
    assert len(promo_starts(changes(50, 0))) == 1


def test_a_deeper_cut_during_a_promo_is_the_same_promo() -> None:
    assert [start.cut for start in promo_starts(changes(0, 20, 50, 0, 30))] == [20, 30]


def test_promo_starts_do_not_depend_on_order() -> None:
    assert len(promo_starts(list(reversed(changes(0, 20, 0, 30))))) == 2


def test_summary_of_nothing() -> None:
    assert history_summary([]) == {
        "lowest_price": None, "lowest_date": None, "promotions": 0,
        "promotions_per_year": 0.0, "average_cut": 0.0, "by_year": [],
    }  # fmt: skip


def test_summary_without_promo() -> None:
    summary = history_summary(changes(0, 0))
    assert (summary["promotions"], summary["average_cut"], summary["lowest_price"]) == (
        0,
        0.0,
        10.0,
    )


@pytest.fixture
def top_game(db: None) -> Game:
    return Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=10)


def run_import(monkeypatch: pytest.MonkeyPatch, *responses: object) -> FakeFetcher:
    fetcher = FakeFetcher(list(responses))
    monkeypatch.setattr(
        import_itad_history, "build_client", lambda key: ItadClient(key, fetch_json=fetcher)
    )
    with override_settings(API_KEYS={"ITAD_API_KEY": "k"}):
        call_command("import_itad_history", limit=1)
    return fetcher


def test_a_known_itad_id_skips_the_lookup(top_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    top_game.itad_id = ITAD_ID
    top_game.save()
    fetcher = run_import(monkeypatch, [deal("2025-02-01T00:00:00+00:00", 5, 10, 50)])
    assert fetcher.calls[0]["id"] == ITAD_ID
    assert PriceChange.objects.count() == 1


def test_a_game_unknown_to_itad_is_skipped(top_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = run_import(monkeypatch, {"found": False})
    top_game.refresh_from_db()
    assert (top_game.itad_id, len(fetcher.calls), PriceChange.objects.count()) == ("", 1, 0)


def test_the_import_is_idempotent(top_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    history = [deal("2025-02-01T00:00:00+00:00", 5, 10, 50)]
    run_import(monkeypatch, {"found": True, "game": {"id": ITAD_ID}}, history)
    run_import(monkeypatch, [deal("2025-02-01T00:00:00+00:00", 4, 10, 60)])
    change = PriceChange.objects.get()
    assert (change.price, change.cut) == (Decimal("4.00"), 60)


def test_france_is_created_for_the_prices(top_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, {"found": False})
    assert Country.objects.filter(iso2="FR").exists()


def test_an_api_error_is_traced(top_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, ApiError("isthereanydeal", "url", "HTTP 401", 401))
    assert "HTTP 401" in ImportRun.objects.get(source="isthereanydeal").errors


def test_unknown_game_history_gives_404(db: None) -> None:
    assert APIClient().get(reverse("stats-price-history", args=[1])).status_code == 404


def test_game_without_history(top_game: Game) -> None:
    data = APIClient().get(reverse("stats-price-history", args=[top_game.appid])).json()
    assert (data["currency"], data["changes"], data["summary"]["promotions"]) == (None, [], 0)


def test_sales_calendar_without_data(db: None) -> None:
    assert APIClient().get(reverse("stats-sales-calendar")).json() == {"years": [], "cells": []}


def test_sales_calendar_adds_up_games_of_the_same_week(db: None) -> None:
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    for appid in (1, 2):
        game = Game.objects.create(appid=appid, name=f"Jeu {appid}")
        for change in changes(0, 50):
            change.game, change.country = game, france
            change.save()
    data = APIClient().get(reverse("stats-sales-calendar")).json()
    assert data == {"years": [2025], "cells": [[2025, 3, 2]]}
