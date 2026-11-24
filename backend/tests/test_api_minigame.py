import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Game
from players.models import PlayerCountSnapshot


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
    for appid, name in ((10, "Counter-Strike"), (20, "Team Fortress Classic")):
        game = Game.objects.create(appid=appid, name=name)
        PlayerCountSnapshot.objects.create(
            game=game, taken_at=timezone.now(), players=100, source="test"
        )
    client = APIClient()
    url = reverse("minigame-duel") + "?metric=players"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "players"
    assert data["game_a"]["appid"] in (10, 20)
    assert data["game_b"]["appid"] in (10, 20)


@pytest.mark.django_db
def test_game_duel_never_invents_a_price():
    for appid in (10, 20, 30):
        Game.objects.create(appid=appid, name=f"Jeu {appid}", is_free=appid != 30)
    data = APIClient().get(reverse("minigame-duel") + "?metric=price_eur").json()
    assert {data["game_a"]["appid"], data["game_b"]["appid"]} == {10, 20}


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["monthly-player-race/?top=abc", "wrapped/?year=abc"])
def test_bad_parameters_do_not_crash(path):
    assert APIClient().get(f"/api/stats/{path}").status_code == 200
