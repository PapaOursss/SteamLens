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
        if "/games/4200/stores" in url:
            return load_fixture("rawg/game_stores")
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


class HomonymFetcher:
    """Deux jeux du même nom : seul le 4200 est vendu sur Steam sous le bon appid."""

    def __init__(self, rawg_ids: list[int]) -> None:
        self._rawg_ids = rawg_ids
        self._real = FakeRawgFetcher()

    def __call__(self, url: str, params: dict[str, str]) -> dict:
        if "/games/9/stores" in url:
            return {"results": [{"store_id": 1, "url": "https://store.steampowered.com/app/400/"}]}
        if "/games/9" in url:
            return {"id": 9, "name": "Portal 2", "rating": 1.0}
        if url.endswith("/games"):
            return {"results": [{"id": rawg_id, "name": "Portal 2"} for rawg_id in self._rawg_ids]}
        return self._real(url, params)


@override_settings(API_KEYS={"RAWG_API_KEY": "fake-key"})
@pytest.mark.parametrize(("rawg_ids", "expected"), [([9, 4200], 4.57), ([9], None)])
def test_only_the_game_with_the_same_appid_is_saved(
    portal_game: Game, monkeypatch: pytest.MonkeyPatch, rawg_ids: list[int], expected: float | None
) -> None:
    client = RawgClient("fake-key", fetch_json=HomonymFetcher(rawg_ids))
    monkeypatch.setattr(import_rawg, "RawgClient", lambda key: client)

    call_command("import_rawg", appid=PORTAL_2)

    portal_game.refresh_from_db()
    assert portal_game.rawg_rating == expected
    assert portal_game.rawg_id == (4200 if expected else None)


@override_settings(API_KEYS={"RAWG_API_KEY": "fake-key"})
def test_an_id_given_to_the_wrong_game_is_taken_back(
    portal_game: Game, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrong = Game.objects.create(appid=400, name="Portal", rawg_id=4200)
    Game.objects.filter(appid=PORTAL_2).update(rawg_id=9)
    client = RawgClient("fake-key", fetch_json=FakeRawgFetcher())
    monkeypatch.setattr(import_rawg, "RawgClient", lambda key: client)

    call_command("import_rawg", appid=PORTAL_2)

    portal_game.refresh_from_db()
    wrong.refresh_from_db()
    assert (portal_game.rawg_id, wrong.rawg_id) == (4200, None)
