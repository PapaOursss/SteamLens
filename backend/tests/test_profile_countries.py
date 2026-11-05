import datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, Genre
from geography.models import ProfileCountryCount, ProfileSample
from ingestion.management.commands import import_profile_countries
from ingestion.sources.steam_reviews import SteamReviewsClient
from ingestion.sources.steam_web_api import NO_COUNTRY, ProfileCountryClient
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

SUMMARIES = "steam_web_api/player_summaries_extract"
RECENT_PAGE = "steam_reviews/recent_413150_page"
DAY = datetime.date(2026, 11, 5)
API_KEYS = {"STEAM_API_KEY": "secret"}


def test_countries_are_counted_without_ids() -> None:
    fetcher = FakeFetcher([load_fixture(SUMMARIES)])
    countries = ProfileCountryClient("secret", fetch_json=fetcher).count_countries(["1", "2"])
    assert countries == {"FR": 1, NO_COUNTRY: 1, "AQ": 1}
    assert fetcher.calls[0]["steamids"] == "1,2"


def test_steamids_are_sent_by_hundred() -> None:
    fetcher = FakeFetcher([{"response": {"players": []}}] * 2)
    ProfileCountryClient("secret", fetch_json=fetcher).count_countries(str(n) for n in range(150))
    assert [len(call["steamids"].split(",")) for call in fetcher.calls] == [100, 50]


@pytest.mark.django_db
@override_settings(API_KEYS=API_KEYS)
def test_import_stores_only_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)
    reviews = FakeFetcher([load_fixture(RECENT_PAGE)])
    summaries = FakeFetcher([load_fixture(SUMMARIES)])
    monkeypatch.setattr(import_profile_countries, "today", lambda: DAY)
    monkeypatch.setattr(
        import_profile_countries,
        "build_clients",
        lambda key: (
            SteamReviewsClient(fetch_json=reviews),
            ProfileCountryClient(key, fetch_json=summaries),
        ),
    )

    call_command("import_profile_countries", limit=1)

    sample = ProfileSample.objects.get()
    assert (sample.profiles, sample.without_country, sample.unmapped_country) == (3, 1, 1)
    assert ProfileCountryCount.objects.get().country_id == "FR"


@pytest.mark.django_db
@override_settings(API_KEYS={"STEAM_API_KEY": ""})
def test_import_is_skipped_without_key() -> None:
    call_command("import_profile_countries")
    assert not ProfileSample.objects.exists()


@pytest.mark.django_db
def test_profile_countries_endpoint_and_map(catalog_sample: dict[str, Game]) -> None:
    stardew = catalog_sample["stardew"]
    ProfileSample.objects.create(game=stardew, date=DAY, profiles=10, without_country=4)
    ProfileCountryCount.objects.create(game=stardew, country_id="FR", date=DAY, profiles=5)
    ProfileCountryCount.objects.create(game=stardew, country_id="US", date=DAY, profiles=1)
    assert Genre.objects.filter(games=stardew).exists()

    data = APIClient().get(reverse("stats-profile-countries")).json()

    assert data["sample"]["without_country_share"] == 0.4
    assert data["countries"][0] == {"iso3": "FRA", "name": "France", "profiles": 5, "share": 0.833}
    assert data["by_genre"][0]["top_country"] == "France"
    world = APIClient().get(reverse("world-map", args=["profile-countries"])).json()
    assert world == {"FRA": 5, "USA": 1}
