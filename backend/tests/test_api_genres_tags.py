from django.test import Client

from catalog.models import Game, GameMode, Genre, Theme


def test_genre_tags_treemap(client: Client, catalog_sample: dict[str, Game]) -> None:
    cs = catalog_sample["counter_strike"]
    cs.owners_mid = 50_000_000
    cs.metacritic_score = 82
    cs.save()

    response = client.get("/api/stats/treemap/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Steam"
    children = data["children"]
    action_node = next((c for c in children if c["name"] == "Action"), None)
    assert action_node is not None
    assert action_node["games"] == 2
    assert action_node["owners"] == 50_000_000
    assert action_node["score"] == 82.0

    fps_child = next((t for t in action_node["children"] if t["name"] == "FPS"), None)
    assert fps_child is not None
    assert fps_child["games"] == 1
    assert fps_child["votes"] == 900
    assert fps_child["score"] == 82.0


def test_sunburst_igdb(client: Client, catalog_sample: dict[str, Game]) -> None:
    stardew = catalog_sample["stardew"]
    igdb_rpg = Genre.objects.create(name="Role-playing (RPG)")
    farming_theme = Theme.objects.create(name="Sandbox")
    coop_mode = GameMode.objects.create(name="Co-operative")

    stardew.igdb_genres.add(igdb_rpg)
    stardew.themes.add(farming_theme)
    stardew.game_modes.add(coop_mode)

    response = client.get("/api/stats/sunburst-igdb/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "IGDB"
    assert len(data["children"]) >= 1

    rpg_node = next((c for c in data["children"] if c["name"] == "Role-playing (RPG)"), None)
    assert rpg_node is not None
    assert rpg_node["value"] == 1
    assert rpg_node["children"][0]["name"] == "Sandbox"
    assert rpg_node["children"][0]["children"][0]["name"] == "Co-operative"
