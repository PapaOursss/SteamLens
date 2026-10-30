import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_steam_wrapped_default():
    client = APIClient()
    url = reverse("stats-wrapped")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert "game_of_the_year" in data
    assert "trending_genre" in data
    assert "biggest_discount" in data
    assert "biggest_flop" in data
    assert "most_expensive_country" in data


@pytest.mark.django_db
def test_steam_wrapped_with_year():
    client = APIClient()
    url = reverse("stats-wrapped") + "?year=2025"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
