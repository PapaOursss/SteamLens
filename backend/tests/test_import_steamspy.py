import pytest
from django.core.management import call_command

from catalog.models import Game, GameTag
from ingestion.http import ApiError
from ingestion.management.commands import import_steamspy
from ingestion.models import ImportRun
from ingestion.sources.steamspy import SteamSpyClient
from players.models import RankingEntry
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

ALL_PAGE = "steamspy/all_page_0_extract"
TOP_100 = "steamspy/top100in2weeks_extract"
DETAILS_730 = "steamspy/appdetails_730"


def use_fake_steamspy(monkeypatch: pytest.MonkeyPatch, pages: list, calls: list) -> FakeFetcher:
    fetcher = FakeFetcher(calls)
    client = SteamSpyClient(fetch_json=fetcher, fetch_all_pages_json=FakeFetcher(pages))
    monkeypatch.setattr(import_steamspy, "build_client", lambda: client)
    return fetcher


@pytest.mark.django_db
def test_imports_catalog_rankings_and_tag_votes(monkeypatch: pytest.MonkeyPatch) -> None:
    details = load_fixture(DETAILS_730)
    fetcher = use_fake_steamspy(
        monkeypatch,
        pages=[load_fixture(ALL_PAGE), {}],
        calls=[load_fixture(TOP_100), load_fixture(TOP_100), details],
    )

    call_command("import_steamspy", details=1)

    assert Game.objects.count() == 3
    counter_strike = Game.objects.get(appid=730)
    assert counter_strike.owners_min == 100_000_000
    assert counter_strike.owners_mid == 150_000_000
    assert counter_strike.is_free
    assert GameTag.objects.get(game=counter_strike, tag__name="FPS").votes == 91172
    assert fetcher.calls[-1] == {"request": "appdetails", "appid": "730"}
    ranks = RankingEntry.objects.filter(chart=RankingEntry.TOP_100_IN_2_WEEKS)
    assert list(ranks.values_list("rank", "game_id")) == [(1, 730), (2, 1172470), (3, 578080)]
    run = ImportRun.objects.get(source="steamspy")
    assert run.succeeded


@pytest.mark.django_db
def test_rerun_keeps_one_ranking_per_day(monkeypatch: pytest.MonkeyPatch) -> None:
    for _ in range(2):
        use_fake_steamspy(monkeypatch, pages=[], calls=[load_fixture(TOP_100), {}])
        call_command("import_steamspy", skip_catalog=True, details=0)

    assert RankingEntry.objects.count() == 3
    assert Game.objects.count() == 3


@pytest.mark.django_db
def test_api_failure_is_recorded_without_crashing(monkeypatch: pytest.MonkeyPatch) -> None:
    failure = ApiError("steamspy", "https://steamspy.com/api.php", "HTTP 500", 500)
    use_fake_steamspy(monkeypatch, pages=[failure], calls=[failure, load_fixture(TOP_100)])

    call_command("import_steamspy", details=0)

    run = ImportRun.objects.get(source="steamspy")
    assert "HTTP 500" in run.errors
    assert RankingEntry.objects.filter(chart=RankingEntry.TOP_100_FOREVER).count() == 3
