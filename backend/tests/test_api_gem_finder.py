import datetime

import pytest
from django.test import Client

from catalog.models import Game, ReviewSummary
from geography.models import Country
from pricing.models import PricePoint


@pytest.mark.django_db
def test_gem_finder_fallback_when_empty(client: Client) -> None:
    response = client.get("/api/stats/gem-finder/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["games"]) >= 4
    assert "Simulation" in data["genres"]
    assert data["gem_criteria"]["max_price"] == 15.0
    assert any(g["is_gem"] for g in data["games"])


@pytest.mark.django_db
def test_gem_finder_with_sample_game(client: Client, catalog_sample: dict[str, Game]) -> None:
    stardew = catalog_sample["stardew"]
    stardew.owners_mid = 100_000
    stardew.save()

    # Review with high satisfaction
    ReviewSummary.objects.create(
        game=stardew,
        language="all",
        positive=950,
        negative=50,
        date=datetime.date(2026, 11, 1),
    )

    response = client.get("/api/stats/gem-finder/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["games"]) >= 1

    sd = next((g for g in data["games"] if g["appid"] == stardew.appid), None)
    assert sd is not None
    assert sd["name"] == "Stardew Valley"
    assert sd["price_eur"] == 13.99
    assert sd["positive_percent"] == 95
    assert sd["genre"] == "Simulation"
    assert sd["year"] == 2016
    assert sd["is_gem"] is True


@pytest.mark.django_db
def test_gem_finder_skips_games_without_price(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    unknown = Game.objects.create(appid=999_001, name="Sans prix", owners_mid=10_000)
    for game in (unknown, catalog_sample["stardew"]):
        game.owners_mid = 10_000
        game.save()
        ReviewSummary.objects.create(
            game=game, language="all", positive=9, negative=1, date=datetime.date(2026, 11, 1)
        )

    games = client.get("/api/stats/gem-finder/").json()["games"]
    assert unknown.appid not in [g["appid"] for g in games]


def add_us_price(game: Game, price_eur: str) -> None:
    usa, _ = Country.objects.get_or_create(iso2="US", iso3="USA", name_fr="États-Unis")
    PricePoint.objects.create(
        game=game, country=usa, currency="USD", price=price_eur, price_eur=price_eur,
        date=datetime.date(2026, 9, 8), source="kaggle_fronkongames",
    )  # fmt: skip


@pytest.mark.django_db
def test_gem_finder_falls_back_on_the_american_price(client: Client) -> None:
    gem = Game.objects.create(appid=999_002, name="Pépite", owners_mid=20_000)
    add_us_price(gem, "4.50")
    ReviewSummary.objects.create(
        game=gem, language="all", positive=480, negative=20, date=datetime.date(2026, 11, 1)
    )

    games = client.get("/api/stats/gem-finder/").json()["games"]

    found = next(g for g in games if g["appid"] == gem.appid)
    assert found["price_eur"] == 4.5
    assert found["is_gem"] is True


@pytest.mark.django_db
def test_gem_finder_needs_enough_reviews_to_judge(client: Client) -> None:
    lucky = Game.objects.create(appid=999_003, name="Trois avis", owners_mid=5_000)
    add_us_price(lucky, "2.00")
    ReviewSummary.objects.create(
        game=lucky, language="all", positive=3, negative=0, date=datetime.date(2026, 11, 1)
    )

    games = client.get("/api/stats/gem-finder/").json()["games"]

    assert lucky.appid not in [g["appid"] for g in games]
