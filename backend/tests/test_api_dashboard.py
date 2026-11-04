from django.test import Client

from catalog.models import Game


def test_dashboard_stats_returns_overview_and_top_games(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    response = client.get("/api/stats/dashboard/")
    assert response.status_code == 200

    body = response.json()
    assert "overview" in body
    assert "top_games" in body
    assert "featured_gem" in body

    overview = body["overview"]
    assert overview["games_count"] == 3
    assert overview["total_players"] == 1_800_000
    assert overview["top_genre"] == "Action"
    assert overview["average_price_eur"] > 0

    top_games = body["top_games"]
    assert len(top_games) == 2
    assert top_games[0]["name"] == "Counter-Strike 2"
    assert top_games[0]["players"] == 1_200_000
    assert "sparkline" in top_games[0]
