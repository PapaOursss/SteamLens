import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game


@pytest.mark.django_db
def test_game_duel_fallback():
    client = APIClient()
    url = reverse("minigame-duel")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "game_a" in data
    assert "game_b" in data
    assert "metric" in data
    assert data["game_a"]["appid"] == 730
    assert data["game_b"]["appid"] == 570


@pytest.mark.django_db
def test_game_duel_with_games():
    Game.objects.create(appid=10, name="Counter-Strike")
    Game.objects.create(appid=20, name="Team Fortress Classic")
    client = APIClient()
    url = reverse("minigame-duel") + "?metric=players"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "players"
    assert data["game_a"]["appid"] in (10, 20)
    assert data["game_b"]["appid"] in (10, 20)
