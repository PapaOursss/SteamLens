import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, Genre, ProtonReport


@pytest.mark.django_db
def test_proton_stats_empty():
    client = APIClient()
    url = reverse("stats-proton")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "tiers" in data
    assert "by_genre" in data


@pytest.mark.django_db
def test_proton_stats_with_data():
    game = Game.objects.create(appid=413150, name="Stardew Valley")
    genre = Genre.objects.create(name="RPG")
    game.genres.add(genre)
    ProtonReport.objects.create(
        game=game, tier="platinum", score=0.98, total_reports=150
    )

    client = APIClient()
    url = reverse("stats-proton")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tiers"]) == 1
    assert data["tiers"][0]["tier"] == "platinum"
    assert len(data["by_genre"]) == 1
    assert data["by_genre"][0]["counts"]["platinum"] == 1
