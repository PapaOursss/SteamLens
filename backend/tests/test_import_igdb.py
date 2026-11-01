import pytest
from django.core.management import call_command
from django.test import override_settings

from catalog.models import Company, Game, IgdbPopularity
from ingestion.http import ApiError
from ingestion.management.commands import import_igdb
from ingestion.models import ImportRun
from ingestion.sources.igdb import IgdbClient, TwitchToken
from tests.fixture_files import load_fixture

WITCHER, WITCHER_GOTY, ELDEN_RING = 292030, 499450, 1245620


class FakeIgdb:
    """Répond aux requêtes IGDB par endpoint et note les corps envoyés."""

    def __init__(self, failures: list[ApiError] | None = None) -> None:
        self.bodies: dict[str, list[str]] = {}
        self.headers: list[dict[str, str]] = []
        self.failures = failures or []

    def __call__(self, url: str, body: str, headers: dict[str, str]) -> list:
        if self.failures:
            raise self.failures.pop(0)
        endpoint = url.rsplit("/", 1)[-1]
        self.bodies.setdefault(endpoint, []).append(body)
        self.headers.append(headers)
        return load_fixture(f"igdb/{endpoint}_extract")


class FakeTokenServer:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, url: str, params: dict[str, str]) -> dict:
        self.calls += 1
        return load_fixture("igdb/token") | {"access_token": f"jeton-{self.calls}"}


@pytest.fixture
def owned_games(db: None) -> None:
    for appid, owners in (
        (WITCHER, 30_000_000),
        (WITCHER_GOTY, 2_000_000),
        (ELDEN_RING, 20_000_000),
    ):
        Game.objects.create(appid=appid, name=str(appid), owners_mid=owners)


def use_fake_igdb(monkeypatch: pytest.MonkeyPatch, igdb: FakeIgdb, tokens: FakeTokenServer) -> None:
    client = IgdbClient(TwitchToken("id-appli", "secret", tokens), igdb)
    monkeypatch.setattr(import_igdb, "build_client", lambda: client)


@pytest.mark.usefixtures("owned_games")
def test_imports_classification_studios_and_popscore(monkeypatch: pytest.MonkeyPatch) -> None:
    igdb, tokens = FakeIgdb(), FakeTokenServer()
    use_fake_igdb(monkeypatch, igdb, tokens)

    call_command("import_igdb")

    assert 'uid = ("292030","1245620","499450")' in igdb.bodies["external_games"][0]
    assert "external_game_source = 1" in igdb.bodies["external_games"][0]
    witcher = Game.objects.get(appid=WITCHER)
    assert witcher.igdb_id == 1942
    assert Game.objects.get(appid=WITCHER_GOTY).igdb_id is None
    assert sorted(witcher.igdb_genres.values_list("name", flat=True)) == [
        "Adventure", "Role-playing (RPG)",
    ]  # fmt: skip
    assert not witcher.genres.exists()
    assert "Open world" in witcher.themes.values_list("name", flat=True)
    assert witcher.player_perspectives.get().name == "Third person"
    assert witcher.developers.get().name == "CD Projekt RED"
    assert Company.objects.get(name="CD Projekt RED").country_id == "PL"
    assert Company.objects.get(name="Studio sans pays").country is None
    goty = Game.objects.get(appid=WITCHER_GOTY)
    assert goty.game_modes.get().name == "Single player"
    elden = Game.objects.get(appid=ELDEN_RING)
    assert sorted(elden.game_modes.values_list("name", flat=True)) == [
        "Co-operative", "Single player",
    ]  # fmt: skip
    assert IgdbPopularity.objects.get(game=witcher, popularity_type="Visits").value == 0.0123
    assert IgdbPopularity.objects.get(game=elden, popularity_type="Playing").value == 0.031
    assert tokens.calls == 1
    assert igdb.headers[0] == {
        "Client-ID": "id-appli", "Authorization": "Bearer jeton-1", "Accept": "application/json",
    }  # fmt: skip
    assert ImportRun.objects.get(source="igdb").succeeded


@pytest.mark.usefixtures("owned_games")
def test_rerun_creates_no_duplicate(monkeypatch: pytest.MonkeyPatch) -> None:
    for _ in range(2):
        use_fake_igdb(monkeypatch, FakeIgdb(), FakeTokenServer())
        call_command("import_igdb")

    assert IgdbPopularity.objects.count() == 5
    assert Game.objects.get(appid=WITCHER).themes.count() == 3


@pytest.mark.usefixtures("owned_games")
def test_an_expired_token_is_renewed_once(monkeypatch: pytest.MonkeyPatch) -> None:
    igdb = FakeIgdb(failures=[ApiError("igdb", "url", "HTTP 401", 401)])
    tokens = FakeTokenServer()
    use_fake_igdb(monkeypatch, igdb, tokens)

    call_command("import_igdb")

    assert tokens.calls == 2
    assert igdb.headers[0]["Authorization"] == "Bearer jeton-2"


def test_the_token_is_renewed_before_it_expires() -> None:
    now = [0.0]
    tokens = FakeTokenServer()
    token = TwitchToken("id", "secret", tokens, clock=lambda: now[0])

    token.value()
    now[0] = 1000.0
    token.value()
    now[0] = 5_011_271.0
    token.value()

    assert tokens.calls == 2


@pytest.mark.django_db
@override_settings(API_KEYS={"TWITCH_CLIENT_ID": "", "TWITCH_CLIENT_SECRET": ""})
def test_without_twitch_keys_the_run_says_why() -> None:
    call_command("import_igdb")

    assert "TWITCH_CLIENT_ID" in ImportRun.objects.get().errors
