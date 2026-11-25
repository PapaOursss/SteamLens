import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, GamePlaytime, Genre
from geography.models import Country
from pricing.models import PricePoint


@pytest.mark.django_db
def test_playtime_stats_empty():
    client = APIClient()
    url = reverse("stats-playtime")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "by_genre" in data
    assert "best_value" in data
    assert len(data["by_genre"]) >= 1


@pytest.mark.django_db
def test_playtime_stats_with_data():
    game = Game.objects.create(appid=413150, name="Stardew Valley")
    genre = Genre.objects.create(name="Farming")
    game.genres.add(genre)
    GamePlaytime.objects.create(
        game=game, median_playtime_minutes=3600, average_playtime_minutes=4200
    )

    unpriced = Game.objects.create(appid=1, name="Sans prix")
    GamePlaytime.objects.create(game=unpriced, median_playtime_minutes=6000)
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    PricePoint.objects.create(
        game=game, country=france, currency="EUR", price=12, price_eur=12,
        date=datetime.date(2026, 10, 1), source="steam_store",
    )  # fmt: skip

    client = APIClient()
    url = reverse("stats-playtime")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    farming_item = next(item for item in data["by_genre"] if item["genre"] == "Farming")
    assert farming_item["median_hours"] == 60.0
    assert len(data["best_value"]) == 1
    assert data["best_value"][0]["appid"] == 413150
