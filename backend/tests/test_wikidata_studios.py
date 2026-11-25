import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Company, Game, Genre
from geography.models import Country
from ingestion.http import ApiError
from ingestion.management.commands import import_wikidata_studios
from ingestion.models import ImportRun
from ingestion.sources.wikidata import WikidataClient
from ingestion.sources.wikidata.studio_query import studio_query
from tests.fixture_files import load_fixture

WITCHER, ELDEN_RING, STARDEW, TERRARIA, BG3 = 292030, 1245620, 413150, 105600, 1086940
MONGOLIA_GAME = 999001

MONGOLIA_STUDIO = {
    "appid": {"type": "literal", "value": str(MONGOLIA_GAME)},
    "developer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q999"},
    "developerLabel": {"type": "literal", "value": "Studio Mongol"},
    "p17_iso2": {"type": "literal", "value": "MN"},
    "p17_iso3": {"type": "literal", "value": "MNG"},
    "p17Label": {"type": "literal", "value": "Mongolie"},
}
UNLABELLED = {
    "appid": {"type": "literal", "value": str(WITCHER)},
    "developer": {"type": "uri", "value": "http://www.wikidata.org/entity/Q12345"},
    "developerLabel": {"type": "literal", "value": "Q12345"},
}


class FakeSparql:
    def __init__(self, failures: list[ApiError] | None = None) -> None:
        self.queries: list[str] = []
        self.failures = failures or []

    def __call__(self, query: str) -> dict:
        if self.failures:
            raise self.failures.pop(0)
        self.queries.append(query)
        body = load_fixture("wikidata/studios_extract")
        body["results"]["bindings"] += [MONGOLIA_STUDIO, UNLABELLED]
        return body


@pytest.fixture
def owned_games(db: None) -> None:
    for appid, owners in (
        (WITCHER, 30_000_000),
        (ELDEN_RING, 20_000_000),
        (STARDEW, 25_000_000),
        (TERRARIA, 28_000_000),
        (BG3, 15_000_000),
        (MONGOLIA_GAME, 1_000),
    ):
        Game.objects.create(appid=appid, name=str(appid), owners_mid=owners)


def use_fake(monkeypatch: pytest.MonkeyPatch, sparql: FakeSparql) -> None:
    monkeypatch.setattr(import_wikidata_studios, "build_client", lambda: WikidataClient(sparql))


def test_query_asks_for_the_appids_and_every_country_path() -> None:
    query = studio_query([730, 570])

    assert 'VALUES ?appid { "730" "570" }' in query
    assert "wdt:P1733" in query and "wdt:P178" in query
    for path in ("wdt:P17 ", "wdt:P495", "wdt:P159/wdt:P17", "wdt:P27"):
        assert path in query


@pytest.mark.usefixtures("owned_games")
def test_import_links_games_to_studios_and_countries(monkeypatch: pytest.MonkeyPatch) -> None:
    sparql = FakeSparql()
    use_fake(monkeypatch, sparql)

    call_command("import_wikidata_studios")

    assert '"292030"' in sparql.queries[0]
    witcher = Game.objects.get(appid=WITCHER)
    assert list(witcher.developers.values_list("name", flat=True)) == ["CD Projekt RED"]
    assert Company.objects.get(name="FromSoftware").country_id == "JP"
    assert Company.objects.get(name="Larian Studios").country_id == "BE"
    assert Company.objects.get(name="Eric Barone").country_id == "US"
    assert Company.objects.get(name="Engine Software").country is None
    terraria = Game.objects.get(appid=TERRARIA)
    assert terraria.developers.count() == 3
    assert not Company.objects.filter(name="Q12345").exists()


@pytest.mark.usefixtures("owned_games")
def test_country_missing_from_the_table_comes_from_wikidata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    use_fake(monkeypatch, FakeSparql())

    call_command("import_wikidata_studios")

    mongolia = Country.objects.get(iso2="MN")
    assert (mongolia.iso3, mongolia.name_fr) == ("MNG", "Mongolie")


@pytest.mark.usefixtures("owned_games")
def test_igdb_country_is_kept_and_names_match_case_insensitively(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    Country.objects.create(iso2="DE", iso3="DEU", name_fr="Allemagne")
    Company.objects.create(name="CD PROJEKT RED", country_id="DE")
    use_fake(monkeypatch, FakeSparql())

    call_command("import_wikidata_studios")
    call_command("import_wikidata_studios")

    assert Company.objects.filter(name__iexact="CD Projekt RED").count() == 1
    assert Company.objects.get(name="CD PROJEKT RED").country_id == "DE"
    assert Game.objects.get(appid=WITCHER).developers.count() == 1


@pytest.mark.usefixtures("owned_games")
def test_api_error_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    use_fake(monkeypatch, FakeSparql(failures=[ApiError("wikidata", "url", "HTTP 500")]))

    call_command("import_wikidata_studios")

    assert "HTTP 500" in ImportRun.objects.get(source="wikidata").errors


@pytest.mark.django_db
def test_api_finds_the_genre_each_country_overrepresents() -> None:
    Country.objects.create(iso2="JP", iso3="JPN", name_fr="Japon")
    Country.objects.create(iso2="US", iso3="USA", name_fr="États-Unis")
    rpg, action = Genre.objects.create(name="RPG"), Genre.objects.create(name="Action")
    japanese = Company.objects.create(name="Studio JP", country_id="JP")
    american = Company.objects.create(name="Studio US", country_id="US")
    for appid in range(1, 7):
        game = Game.objects.create(appid=appid, name=f"JP {appid}")
        game.developers.add(japanese)
        game.genres.add(action, *([rpg] if appid <= 4 else []))
    for appid in range(11, 21):
        game = Game.objects.create(appid=appid, name=f"US {appid}")
        game.developers.add(american)
        game.genres.add(action)

    data = APIClient().get("/api/stats/studio-countries/").json()

    assert data["is_sample"] is False
    usa, japan = data["countries"]
    assert (usa["iso3"], usa["games"], usa["studios"]) == ("USA", 10, 1)
    assert japan["favorite_genre"] == "RPG"
    assert japan["favorite_index"] == 2.67
    assert usa["favorite_genre"] == "Action"
    assert japan["top_studios"] == [{"name": "Studio JP", "games": 6}]


@pytest.mark.django_db
def test_api_says_when_it_is_a_sample() -> None:
    assert APIClient().get("/api/stats/studio-countries/").json()["is_sample"] is True
