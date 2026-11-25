import datetime

import pytest
from django.test import Client

from catalog.models import Game, ReviewSummary
from geography.country_table import BY_ISO2
from geography.language_table import COUNTRY_LANGUAGES
from geography.models import Country, CountryIndicator

URL = "/api/stats/genres-by-country/"
DAY = datetime.date(2026, 11, 1)


def add_reviews(game: Game, language: str, positive: int, day: datetime.date = DAY) -> None:
    ReviewSummary.objects.create(game=game, language=language, positive=positive, date=day)


@pytest.fixture
def reviews(catalog_sample: dict[str, Game]) -> None:
    action, farm = catalog_sample["counter_strike"], catalog_sample["stardew"]
    add_reviews(action, "russian", 900)
    add_reviews(farm, "russian", 100)
    add_reviews(action, "japanese", 100)
    add_reviews(farm, "japanese", 900)


def by_iso3(client: Client) -> dict[str, dict]:
    return {row["iso3"]: row for row in client.get(URL).json()["countries"]}


def test_dominant_genre_is_relative_to_the_world(client: Client, reviews: None) -> None:
    countries = by_iso3(client)

    assert countries["RUS"]["dominant"] == "Action"
    assert countries["RUS"]["genres"][0]["index"] == 1.8
    assert countries["JPN"]["dominant"] == "Simulation"


def test_only_the_latest_summary_counts(
    client: Client, reviews: None, catalog_sample: dict[str, Game]
) -> None:
    add_reviews(catalog_sample["stardew"], "russian", 8100, DAY + datetime.timedelta(days=1))

    shares = {row["genre"]: row["share"] for row in by_iso3(client)["RUS"]["genres"]}
    assert shares["Simulation"] == pytest.approx(0.9)


def test_reviews_follow_the_population(client: Client, reviews: None) -> None:
    for iso2, population in (("RU", 300.0), ("BY", 100.0), ("KZ", 100.0)):
        row = BY_ISO2[iso2]
        Country.objects.create(iso2=iso2, iso3=row.iso3, name_fr=row.name_fr)
        CountryIndicator.objects.create(
            country_id=iso2, indicator=CountryIndicator.POPULATION, year=2025, value=population
        )

    assert by_iso3(client)["RUS"]["reviews"] == 600


def test_without_reviews_the_map_is_empty(client: Client, db: None) -> None:
    assert client.get(URL).json() == {"genres": [], "countries": []}


def test_every_country_is_known_and_whole() -> None:
    assert set(COUNTRY_LANGUAGES) <= set(BY_ISO2)
    assert all(sum(parts.values()) == pytest.approx(1) for parts in COUNTRY_LANGUAGES.values())
