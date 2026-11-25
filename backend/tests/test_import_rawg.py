import pytest
from django.core.management import call_command
from django.test import override_settings

from catalog.models import Game, GamePlaytime
from ingestion.management.commands import import_rawg
from ingestion.sources.rawg import RawgClient
from tests.fixture_files import load_fixture

PORTAL_2 = 620


class FakeRawgFetcher:
    def __call__(self, url: str, params: dict[str, str]) -> dict:
        if "/games/4200/screenshots" in url:
            return load_fixture("rawg/game_screenshots")
        if "/games/4200" in url:
            return load_fixture("rawg/game_details")
        return load_fixture("rawg/game_search")


@pytest.fixture
def portal_game(db: None) -> Game:
    return Game.objects.create(appid=PORTAL_2, name="Portal 2", owners_mid=10_000_000)


@override_settings(API_KEYS={"RAWG_API_KEY": "fake-key"})
def test_import_rawg_enriches_game(portal_game: Game, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = RawgClient("fake-key", fetch_json=FakeRawgFetcher())
    monkeypatch.setattr(import_rawg, "RawgClient", lambda *args, **kwargs: fake_client)

    call_command("import_rawg", appid=PORTAL_2)

    portal_game.refresh_from_db()
    assert portal_game.rawg_id == 4200
    assert portal_game.rawg_rating == 4.57
    assert portal_game.metacritic_score == 95
    assert len(portal_game.screenshots) >= 2

    # Playtime
    playtime = GamePlaytime.objects.get(game=portal_game)
    assert playtime.average_playtime_minutes == 11 * 60

    # Tags
    tags = list(portal_game.tags.values_list("name", flat=True))
    assert "Singleplayer" in tags
    assert "Co-op" in tags
