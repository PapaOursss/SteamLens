import datetime

import pytest
from django.test import Client

from catalog.models import Game, ReviewSummary


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
