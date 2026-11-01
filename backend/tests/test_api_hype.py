import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Game
from players.models import PlayerCountSnapshot, TwitchStreamSnapshot


@pytest.mark.django_db
def test_hype_stats_fallback():
    client = APIClient()
    url = reverse("stats-hype")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "watched_more" in data
    assert "played_in_silence" in data
    assert len(data["watched_more"]) >= 1


@pytest.mark.django_db
def test_hype_stats_with_data():
    now = timezone.now()
    game = Game.objects.create(appid=730, name="CS2")
    PlayerCountSnapshot.objects.create(
        game=game, taken_at=now, players=1000000, source="steam"
    )
    TwitchStreamSnapshot.objects.create(
        game=game, taken_at=now, viewer_count=50000, stream_count=100
    )

    client = APIClient()
    url = reverse("stats-hype")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "watched_more" in data
    assert "played_in_silence" in data
