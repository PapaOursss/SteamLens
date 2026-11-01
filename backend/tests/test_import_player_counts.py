import datetime

import pytest
from django.core.management import call_command

from catalog.models import Game
from ingestion.http import ApiError
from ingestion.management.commands import import_steamcharts_history, snapshot_players
from ingestion.models import ImportRun
from ingestion.sources.steam_web_api import PlayerCountClient
from ingestion.sources.steamcharts import SteamChartsClient
from players.models import PlayerCountSnapshot
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

TAKEN_AT = datetime.datetime(2026, 11, 1, 14, 0, tzinfo=datetime.UTC)
KNOWN_GAME = "steam_web_api/current_players_730"
UNKNOWN_GAME = "steam_web_api/current_players_unknown"
CHART = "steamcharts/chart_data_413150_extract"


@pytest.fixture
def ranked_games(db: None) -> None:
    Game.objects.create(appid=730, name="Counter-Strike 2", owners_mid=150_000_000)
    Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)
    Game.objects.create(appid=999, name="Sans propriétaires connus")


def fake_players(monkeypatch: pytest.MonkeyPatch, *responses: object) -> FakeFetcher:
    fetcher = FakeFetcher(list(responses))
    monkeypatch.setattr(snapshot_players, "run_timestamp", lambda: TAKEN_AT)
    monkeypatch.setattr(
        snapshot_players,
        "build_client",
        lambda taken_at: PlayerCountClient(fetch_json=fetcher, now=lambda: taken_at),
    )
    return fetcher


@pytest.mark.usefixtures("ranked_games")
def test_snapshot_photographs_the_most_owned_games(monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = fake_players(monkeypatch, load_fixture(KNOWN_GAME), load_fixture(UNKNOWN_GAME))

    call_command("snapshot_players")

    assert [call["appid"] for call in fetcher.calls] == ["730", "413150"]
    snapshot = PlayerCountSnapshot.objects.get()
    assert (snapshot.game_id, snapshot.players, snapshot.taken_at) == (730, 656246, TAKEN_AT)
    assert ImportRun.objects.get(source="snapshot_players").rows == 1


@pytest.mark.usefixtures("ranked_games")
def test_snapshot_twice_in_the_same_minute_keeps_one_row(monkeypatch: pytest.MonkeyPatch) -> None:
    for _ in range(2):
        fake_players(monkeypatch, load_fixture(KNOWN_GAME), load_fixture(KNOWN_GAME))
        call_command("snapshot_players", limit=1)

    assert PlayerCountSnapshot.objects.count() == 1


@pytest.mark.usefixtures("ranked_games")
def test_snapshot_records_errors_and_goes_on(monkeypatch: pytest.MonkeyPatch) -> None:
    failure = ApiError("steam_web_api", "url", "HTTP 500", 500)
    fake_players(monkeypatch, failure, load_fixture(KNOWN_GAME))

    call_command("snapshot_players")

    assert PlayerCountSnapshot.objects.get().game_id == 413150
    assert "HTTP 500" in ImportRun.objects.get().errors


@pytest.mark.django_db
def test_snapshot_without_ranked_games_says_what_to_run(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_players(monkeypatch)

    call_command("snapshot_players")

    assert "import_steamspy" in ImportRun.objects.get().errors


@pytest.mark.usefixtures("ranked_games")
def test_steamcharts_history_fills_the_past(monkeypatch: pytest.MonkeyPatch) -> None:
    not_tracked = ApiError("steamcharts", "url", "HTTP 404", 404)
    fetcher = FakeFetcher([not_tracked, load_fixture(CHART)])
    client = SteamChartsClient(fetch_json=fetcher)
    monkeypatch.setattr(import_steamcharts_history, "build_client", lambda: client)

    call_command("import_steamcharts_history")
    monkeypatch.setattr(
        import_steamcharts_history,
        "build_client",
        lambda: SteamChartsClient(fetch_json=FakeFetcher([not_tracked, load_fixture(CHART)])),
    )
    call_command("import_steamcharts_history", limit=2)

    points = PlayerCountSnapshot.objects.filter(game_id=413150, source="steamcharts")
    assert points.count() == 6
    first = points.order_by("taken_at").first()
    assert first.taken_at == datetime.datetime(2015, 12, 1, tzinfo=datetime.UTC)
