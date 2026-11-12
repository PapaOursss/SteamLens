import datetime

import pytest
from django.test import Client

from catalog.models import Game, Genre


@pytest.mark.django_db
def test_genre_streamgraph_endpoint_empty(client: Client) -> None:
    response = client.get("/api/stats/streamgraph/")
    assert response.status_code == 200
    data = response.json()
    assert data["years"] == []
    assert data["genres"] == []
    assert data["series"] == []
    assert len(data["events"]) == 3


def test_genre_streamgraph_endpoint_with_data(client: Client, catalog_sample: dict[str, Game]) -> None:
    action = Genre.objects.get(name="Action")
    simulation = Genre.objects.get(name="Simulation")

    # Counter-Strike 2 release in 2012
    cs = catalog_sample["counter_strike"]
    cs.release_date = datetime.date(2012, 8, 21)
    cs.save()

    # Dota 2 in 2013
    dota = catalog_sample["dota"]
    dota.release_date = datetime.date(2013, 7, 9)
    dota.save()

    # Stardew Valley in 2016
    stardew = catalog_sample["stardew"]
    stardew.release_date = datetime.date(2016, 2, 26)
    stardew.save()

    # Create another game in 2016 with Action
    g = Game.objects.create(appid=99999, name="Action Game 2016", release_date=datetime.date(2016, 5, 1))
    g.genres.add(action)

    response = client.get("/api/stats/streamgraph/")
    assert response.status_code == 200
    data = response.json()

    assert data["years"] == [2012, 2013, 2016]
    assert "Action" in data["genres"]
    assert "Simulation" in data["genres"]

    action_idx = data["genres"].index("Action")
    sim_idx = data["genres"].index("Simulation")

    # In 2012: CS (Action), 2013: Dota (Action), 2016: Action Game (Action)
    assert data["series"][action_idx] == [1, 1, 1]
    # In 2012: 0, 2013: 0, 2016: Stardew (Simulation)
    assert data["series"][sim_idx] == [0, 0, 1]

    assert len(data["events"]) == 3
    assert data["events"][0]["year"] == 2012
