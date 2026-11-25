import pytest
from rest_framework.test import APIClient

from catalog.models import Game, ReviewSummary
from ingestion.writing.game_writer import ALL_LANGUAGES


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def comparison_data(db: None) -> None:
    game1 = Game.objects.create(
        appid=10,
        name="Counter-Strike",
        metacritic_score=88,
        rawg_rating=4.2,
    )
    ReviewSummary.objects.create(
        game=game1,
        language=ALL_LANGUAGES,
        positive=900,
        negative=100,
        date="2026-01-01",
    )

    game2 = Game.objects.create(
        appid=20,
        name="Team Fortress Classic",
        metacritic_score=None,
    )
    ReviewSummary.objects.create(
        game=game2,
        language=ALL_LANGUAGES,
        positive=80,
        negative=20,
        date="2026-01-01",
    )


def test_rating_comparison_endpoint(api_client: APIClient, comparison_data: None) -> None:
    response = api_client.get("/api/stats/rating-comparison/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["appid"] == 10
    assert data[0]["name"] == "Counter-Strike"
    assert data[0]["press_score"] == 88
    assert data[0]["steam_score"] == 90.0
    assert data[0]["rawg_rating"] == 4.2
