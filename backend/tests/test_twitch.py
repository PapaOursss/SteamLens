from datetime import UTC, datetime

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Game
from ingestion.http import ApiError
from ingestion.management.commands import snapshot_twitch
from ingestion.models import ImportRun
from ingestion.sources.igdb import TwitchToken
from ingestion.sources.twitch import HelixClient
from ingestion.sources.twitch.steam_match import normalize_name
from players.models import (
    TwitchCategory,
    TwitchLanguageDay,
    TwitchMonth,
    TwitchStreamSnapshot,
    TwitchTopSnapshot,
)
from tests.fixture_files import FIXTURES_DIR, load_fixture

GTA, ELDEN_RING, DOTA = 271590, 1245620, 570
HISTORY = FIXTURES_DIR / "kaggle" / "twitch_game_data_extract.csv"


class FakeHelix:
    """Répond à Helix par endpoint ; seul GTA V a des streams, sur deux pages."""

    def __init__(self, failures: list[ApiError] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.headers: list[dict[str, str]] = []
        self.failures = failures or []

    def __call__(self, url: str, params: dict, headers: dict[str, str]) -> dict:
        if self.failures:
            raise self.failures.pop(0)
        endpoint = url.removeprefix("https://api.twitch.tv/helix/")
        self.calls.append((endpoint, params))
        self.headers.append(headers)
        if endpoint == "games/top":
            return load_fixture("twitch/games_top")
        if params["game_id"] != "32982":
            return {"data": [], "pagination": {}}
        page = "streams_page2" if params.get("after") == "page-2" else "streams_page1"
        return load_fixture(f"twitch/{page}")


class FakeTokenServer:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, url: str, params: dict[str, str]) -> dict:
        self.calls += 1
        return {"access_token": f"jeton-{self.calls}", "expires_in": 5000000}


@pytest.fixture
def steam_games(db: None) -> None:
    Game.objects.create(appid=GTA, name="Grand Theft Auto V Legacy", igdb_id=1020, owners_mid=50)
    Game.objects.create(appid=ELDEN_RING, name="ELDEN RING™", owners_mid=20)
    Game.objects.create(appid=DOTA, name="Dota 2", owners_mid=100)


def use_fake_helix(monkeypatch: pytest.MonkeyPatch, helix: FakeHelix) -> FakeTokenServer:
    tokens = FakeTokenServer()
    client = HelixClient(TwitchToken("id-appli", "secret", tokens), helix)
    monkeypatch.setattr(snapshot_twitch, "build_client", lambda: client)
    return tokens


def freeze_hour(monkeypatch: pytest.MonkeyPatch, hour: int) -> None:
    moment = datetime(2026, 11, 25, hour, 17, tzinfo=UTC)
    monkeypatch.setattr(snapshot_twitch.timezone, "now", lambda: moment)


@pytest.mark.usefixtures("steam_games")
def test_snapshot_keeps_ranks_viewers_and_languages(monkeypatch: pytest.MonkeyPatch) -> None:
    helix = FakeHelix()
    use_fake_helix(monkeypatch, helix)
    freeze_hour(monkeypatch, 9)

    call_command("snapshot_twitch")

    gta = TwitchTopSnapshot.objects.get(category_id="32982")
    assert (gta.rank, gta.viewer_count, gta.stream_count) == (2, 9500, 4)
    assert gta.taken_at == datetime(2026, 11, 25, 9, tzinfo=UTC)
    hours = dict(
        TwitchLanguageDay.objects.filter(category_id="32982").values_list(
            "language", "viewer_hours"
        )
    )
    assert hours == {"en": 6000, "fr": 3000, "other": 500}
    assert ("streams", {"game_id": "32982", "first": 100, "after": "page-2"}) in helix.calls
    assert helix.headers[0] == {"Client-Id": "id-appli", "Authorization": "Bearer jeton-1"}


@pytest.mark.usefixtures("steam_games")
def test_categories_are_linked_to_steam_by_igdb_then_by_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_fake_helix(monkeypatch, FakeHelix())
    freeze_hour(monkeypatch, 9)

    call_command("snapshot_twitch")

    assert TwitchCategory.objects.get(twitch_id="32982").game_id == GTA
    assert TwitchCategory.objects.get(twitch_id="512953").game_id == ELDEN_RING
    assert TwitchCategory.objects.get(twitch_id="509658").game_id is None
    assert TwitchCategory.objects.get(twitch_id="509658").box_art_url.endswith("509658-144x192.jpg")
    assert TwitchStreamSnapshot.objects.get(game_id=GTA).viewer_count == 9500


@pytest.mark.usefixtures("steam_games")
def test_same_hour_twice_does_not_count_languages_twice(monkeypatch: pytest.MonkeyPatch) -> None:
    use_fake_helix(monkeypatch, FakeHelix())
    freeze_hour(monkeypatch, 9)
    call_command("snapshot_twitch")
    call_command("snapshot_twitch")
    freeze_hour(monkeypatch, 10)
    call_command("snapshot_twitch")

    assert TwitchTopSnapshot.objects.filter(category_id="32982").count() == 2
    assert TwitchLanguageDay.objects.get(category_id="32982", language="en").viewer_hours == 12000


@pytest.mark.usefixtures("steam_games")
def test_expired_token_is_renewed_once(monkeypatch: pytest.MonkeyPatch) -> None:
    helix = FakeHelix(failures=[ApiError("twitch", "url", "HTTP 401", 401)])
    tokens = use_fake_helix(monkeypatch, helix)
    freeze_hour(monkeypatch, 9)

    call_command("snapshot_twitch")

    assert tokens.calls == 2
    assert helix.headers[0]["Authorization"] == "Bearer jeton-2"


@pytest.mark.django_db
def test_missing_keys_skip_the_source(settings) -> None:
    settings.API_KEYS = {}

    call_command("snapshot_twitch")

    run = ImportRun.objects.get(source="twitch")
    assert "TWITCH_CLIENT_ID" in run.errors
    assert not TwitchTopSnapshot.objects.exists()


def test_names_match_despite_case_and_trademarks() -> None:
    assert normalize_name("ELDEN RING™") == normalize_name("Elden  Ring")
    assert normalize_name("Baldur’s Gate 3") == normalize_name("Baldur's Gate 3")


@pytest.mark.usefixtures("steam_games")
def test_history_import_keeps_one_row_per_game_and_month() -> None:
    call_command("import_kaggle_twitch", file=HISTORY)
    call_command("import_kaggle_twitch", file=HISTORY)

    assert TwitchMonth.objects.count() == 7
    dota = TwitchMonth.objects.get(name="Dota 2", month="2024-09-01")
    assert (dota.rank, dota.avg_viewers, dota.game_id) == (9, 45000, DOTA)
    assert TwitchMonth.objects.get(name="Pokémon Legends: Arceus").hours_watched == 18836190
    assert TwitchMonth.objects.get(name="Just Chatting").game_id is None


@pytest.mark.usefixtures("steam_games")
def test_api_serves_latest_top_and_language_shares(monkeypatch: pytest.MonkeyPatch) -> None:
    use_fake_helix(monkeypatch, FakeHelix())
    freeze_hour(monkeypatch, 9)
    call_command("snapshot_twitch")

    data = APIClient().get("/api/stats/twitch/").json()

    assert data["is_sample"] is False
    assert [row["name"] for row in data["top"]] == [
        "Just Chatting",
        "Grand Theft Auto V",
        "ELDEN RING",
    ]
    assert data["top"][1]["appid"] == GTA
    assert data["languages"][0] == {"language": "en", "share": 63.2}


@pytest.mark.usefixtures("steam_games")
def test_api_history_feeds_the_race() -> None:
    call_command("import_kaggle_twitch", file=HISTORY)

    data = APIClient().get("/api/stats/twitch-history/?top=3").json()

    assert data["is_sample"] is False
    assert data["months"] == ["2016-01", "2024-09"]
    assert [row["name"] for row in data["timeline"]["2016-01"]] == [
        "League of Legends", "Counter-Strike: Global Offensive", "Dota 2",
    ]  # fmt: skip
    assert data["timeline"]["2016-01"][2]["appid"] == DOTA


@pytest.mark.django_db
def test_api_says_when_it_is_a_sample() -> None:
    client = APIClient()

    assert client.get("/api/stats/twitch/").json()["is_sample"] is True
    assert client.get("/api/stats/twitch-history/").json()["is_sample"] is True
