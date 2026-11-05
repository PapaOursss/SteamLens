import datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, Genre
from geography.models import Country, ProfileCountryCount, ProfileSample
from ingestion.http import ApiError
from ingestion.management.commands import import_profile_countries
from ingestion.models import ImportRun
from ingestion.sources.steam_reviews import SteamReviewsClient
from ingestion.sources.steam_web_api import NO_COUNTRY, ProfileCountryClient
from tests.fake_fetcher import FakeFetcher

DAY = datetime.date(2026, 11, 5)
TIMESTAMP = 1793865600


def players(*codes: str | None) -> dict:
    rows = [{"steamid": str(n)} | ({"loccountrycode": code} if code else {})
            for n, code in enumerate(codes)]  # fmt: skip
    return {"response": {"players": rows}}


def count(*responses: object, steamids: list[str] | None = None) -> dict[str, int]:
    fetcher = FakeFetcher(list(responses))
    return dict(ProfileCountryClient("key", fetch_json=fetcher).count_countries(steamids or ["1"]))


def test_codes_are_uppercased() -> None:
    assert count(players("fr", "FR")) == {"FR": 2}


def test_empty_code_counts_as_no_country() -> None:
    assert count(players("", None)) == {NO_COUNTRY: 2}


def test_missing_players_give_nothing() -> None:
    assert count({"response": {}}) == {}
    assert count({}) == {}


def test_no_steamid_means_no_request() -> None:
    fetcher = FakeFetcher([])
    assert ProfileCountryClient("key", fetch_json=fetcher).count_countries([]) == {}
    assert fetcher.calls == []


def test_the_key_is_sent() -> None:
    fetcher = FakeFetcher([players("FR")])
    ProfileCountryClient("my-key", fetch_json=fetcher).count_countries(["7"])
    assert fetcher.calls == [{"key": "my-key", "steamids": "7"}]


def test_batches_are_summed() -> None:
    steamids = [str(n) for n in range(101)]
    assert count(players("FR"), players("FR", "DE"), steamids=steamids) == {"FR": 2, "DE": 1}


def recent_page(*steamids: str) -> dict:
    reviews = [{"author": {"steamid": steamid}, "timestamp_created": TIMESTAMP, "voted_up": True}
               for steamid in steamids]  # fmt: skip
    return {"success": 1, "reviews": reviews, "cursor": "*"}


def run_import(monkeypatch: pytest.MonkeyPatch, reviews: list, summaries: list) -> FakeFetcher:
    summary_fetcher = FakeFetcher(summaries)
    monkeypatch.setattr(import_profile_countries, "today", lambda: DAY)
    monkeypatch.setattr(
        import_profile_countries,
        "build_clients",
        lambda key: (
            SteamReviewsClient(fetch_json=FakeFetcher(reviews)),
            ProfileCountryClient(key, fetch_json=summary_fetcher),
        ),
    )
    with override_settings(API_KEYS={"STEAM_API_KEY": "key"}):
        call_command("import_profile_countries", limit=1)
    return summary_fetcher


@pytest.fixture
def ranked_game(db: None) -> Game:
    return Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=1)


@pytest.mark.usefixtures("ranked_game")
def test_an_author_with_two_reviews_is_counted_once(monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = run_import(monkeypatch, [recent_page("1", "1", "2")], [players("FR", "FR")])
    assert sorted(fetcher.calls[0]["steamids"].split(",")) == ["1", "2"]


@pytest.mark.usefixtures("ranked_game")
def test_reviews_without_author_are_left_out(monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = run_import(monkeypatch, [recent_page("", "5")], [players("FR")])
    assert fetcher.calls[0]["steamids"] == "5"


@pytest.mark.usefixtures("ranked_game")
def test_no_review_gives_an_empty_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, [recent_page()], [])
    sample = ProfileSample.objects.get()
    assert (sample.profiles, sample.without_country) == (0, 0)
    assert not ProfileCountryCount.objects.exists()


@pytest.mark.usefixtures("ranked_game")
def test_known_countries_are_created_on_the_fly(monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, [recent_page("1", "2")], [players("JP", "JP")])
    assert Country.objects.get(iso2="JP").iso3 == "JPN"
    assert ProfileCountryCount.objects.get().profiles == 2


@pytest.mark.usefixtures("ranked_game")
def test_a_rerun_the_same_day_replaces_the_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, [recent_page("1")], [players("FR")])
    run_import(monkeypatch, [recent_page("1", "2")], [players("FR", "FR")])
    assert ProfileSample.objects.get().profiles == 2
    assert ProfileCountryCount.objects.get().profiles == 2


@pytest.mark.usefixtures("ranked_game")
def test_an_api_error_is_traced(monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, [ApiError("steam_reviews", "url", "HTTP 429", 429)], [])
    assert "HTTP 429" in ImportRun.objects.get(source="steam_profiles").errors
    assert not ProfileSample.objects.exists()


@pytest.mark.usefixtures("ranked_game")
def test_nothing_identifies_a_player(monkeypatch: pytest.MonkeyPatch) -> None:
    run_import(monkeypatch, [recent_page("76561198000000001")], [players("FR")])
    for model in (ProfileSample, ProfileCountryCount):
        stored = [str(value) for row in model.objects.values() for value in row.values()]
        assert not any("76561198" in value for value in stored)


def test_endpoint_without_sample(db: None) -> None:
    data = APIClient().get(reverse("stats-profile-countries")).json()
    assert data["sample"]["profiles"] == 0
    assert data["sample"]["without_country_share"] == 0.0
    assert (data["countries"], data["by_genre"]) == ([], [])


def test_map_without_sample_is_empty(db: None) -> None:
    assert APIClient().get(reverse("world-map", args=["profile-countries"])).json() == {}


def test_only_the_latest_day_is_shown(catalog_sample: dict[str, Game]) -> None:
    stardew = catalog_sample["stardew"]
    for day, profiles in ((datetime.date(2026, 10, 1), 50), (DAY, 3)):
        ProfileSample.objects.create(game=stardew, date=day, profiles=profiles)
        ProfileCountryCount.objects.create(game=stardew, country_id="FR", date=day,
                                           profiles=profiles)  # fmt: skip
    data = APIClient().get(reverse("stats-profile-countries")).json()
    assert data["sample"]["profiles"] == 3
    world = APIClient().get(reverse("world-map", args=["profile-countries"])).json()
    assert world == {"FRA": 3}


def test_samples_of_several_games_are_summed(catalog_sample: dict[str, Game]) -> None:
    for game in catalog_sample.values():
        ProfileSample.objects.create(game=game, date=DAY, profiles=10, without_country=5,
                                     unmapped_country=1)  # fmt: skip
        ProfileCountryCount.objects.create(game=game, country_id="US", date=DAY, profiles=4)
    data = APIClient().get(reverse("stats-profile-countries")).json()
    assert data["sample"] == {
        "date": "2026-11-05", "games": 3, "profiles": 30, "without_country": 15,
        "without_country_share": 0.5, "unmapped_country": 3,
    }  # fmt: skip
    assert data["countries"] == [
        {"iso3": "USA", "name": "États-Unis", "profiles": 12, "share": 1.0}
    ]


def test_dominant_country_per_genre(catalog_sample: dict[str, Game]) -> None:
    ProfileSample.objects.create(game=catalog_sample["counter_strike"], date=DAY, profiles=9)
    ProfileCountryCount.objects.create(game=catalog_sample["counter_strike"], country_id="FR",
                                       date=DAY, profiles=2)  # fmt: skip
    ProfileCountryCount.objects.create(game=catalog_sample["counter_strike"], country_id="US",
                                       date=DAY, profiles=6)  # fmt: skip
    data = APIClient().get(reverse("stats-profile-countries")).json()
    action = Genre.objects.get(name="Action").name
    assert data["by_genre"] == [
        {"genre": action, "profiles": 8, "top_country": "États-Unis", "top_country_share": 0.75}
    ]
