import pytest
from django.test import Client

from catalog.models import Game, GameTag, Tag


@pytest.mark.django_db
def test_tag_network_empty(client: Client) -> None:
    response = client.get("/api/stats/tag-network/")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["nodes"] == []
    assert data["edges"] == []


@pytest.mark.django_db
def test_tag_network_with_cooccurrences(client: Client) -> None:
    g1 = Game.objects.create(appid=1001, name="Game One")
    g2 = Game.objects.create(appid=1002, name="Game Two")

    t_rpg = Tag.objects.create(name="RPG")
    t_action = Tag.objects.create(name="Action")
    t_cozy = Tag.objects.create(name="Cozy")

    # g1 has RPG and Action
    GameTag.objects.create(game=g1, tag=t_rpg, votes=10)
    GameTag.objects.create(game=g1, tag=t_action, votes=15)

    # g2 has RPG and Action and Cozy
    GameTag.objects.create(game=g2, tag=t_rpg, votes=5)
    GameTag.objects.create(game=g2, tag=t_action, votes=8)
    GameTag.objects.create(game=g2, tag=t_cozy, votes=2)

    response = client.get("/api/stats/tag-network/")
    assert response.status_code == 200
    data = response.json()

    assert len(data["nodes"]) == 3
    node_names = {n["name"] for n in data["nodes"]}
    assert node_names == {"RPG", "Action", "Cozy"}

    # RPG and Action co-occur twice (weight = 2 >= MIN_EDGE_WEIGHT)
    assert len(data["edges"]) == 1
    edge = data["edges"][0]
    assert edge["weight"] == 2
    edge_tag_ids = {edge["source"], edge["target"]}
    assert edge_tag_ids == {t_rpg.id, t_action.id}

    # Verify community assignments
    for node in data["nodes"]:
        assert "community" in node


def _tag_games(tag_names: list[str], first_appid: int, games_count: int) -> None:
    tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
    for offset in range(games_count):
        game = Game.objects.create(appid=first_appid + offset, name=f"Jeu {first_appid + offset}")
        GameTag.objects.bulk_create(GameTag(game=game, tag=tag, votes=1) for tag in tags)


@pytest.mark.django_db
def test_tag_network_links_niche_tags_and_splits_families(client: Client) -> None:
    _tag_games(["Action", "Strategy", "War", "Tactical"], first_appid=2001, games_count=3)
    _tag_games(["Action", "Cozy", "Farming", "Cute"], first_appid=2101, games_count=3)

    data = client.get("/api/stats/tag-network/").json()

    linked = {edge["source"] for edge in data["edges"]} | {edge["target"] for edge in data["edges"]}
    assert linked == {node["id"] for node in data["nodes"]}
    community = {node["name"]: node["community"] for node in data["nodes"]}
    assert community["Strategy"] == community["War"] == community["Tactical"]
    assert community["Cozy"] == community["Farming"] == community["Cute"]
    assert community["Strategy"] != community["Cozy"]
