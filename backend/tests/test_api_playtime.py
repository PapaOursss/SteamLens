import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, GamePlaytime, Genre


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

    client = APIClient()
    url = reverse("stats-playtime")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    farming_item = next(item for item in data["by_genre"] if item["genre"] == "Farming")
    assert farming_item["median_hours"] == 60.0
    assert len(data["best_value"]) == 1
    assert data["best_value"][0]["appid"] == 413150
