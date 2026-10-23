from django.test import Client

from catalog.models import Game


def test_genre_stats_count_the_games(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get("/api/stats/genres/").json()

    assert body == [{"name": "Action", "games": 2}, {"name": "Simulation", "games": 1}]


def test_tag_stats_sum_the_votes(client: Client, catalog_sample: dict[str, Game]) -> None:
    body = client.get("/api/stats/tags/").json()

    assert body == [
        {"name": "Cozy", "games": 1, "votes": 300},
        {"name": "FPS", "games": 1, "votes": 900},
    ]


def test_top_played_uses_the_latest_snapshot(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    body = client.get("/api/stats/top-played/?limit=5").json()

    assert [(game["name"], game["players"]) for game in body] == [
        ("Counter-Strike 2", 1_200_000),
        ("Dota 2", 600_000),
    ]


def test_top_played_respects_the_limit(client: Client, catalog_sample: dict[str, Game]) -> None:
    assert len(client.get("/api/stats/top-played/?limit=1").json()) == 1
