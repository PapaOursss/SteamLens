import datetime
from django.test import Client

from catalog.models import Game


def test_release_calendar_fallback_when_empty(client: Client) -> None:
    response = client.get("/api/stats/release-calendar/")
    assert response.status_code == 200
    data = response.json()
    assert "weekday_month" in data
    assert "daily_contributions" in data
    assert len(data["weekday_month"]) == 84  # 7 days x 12 months
    assert len(data["days"]) == 7
    assert len(data["months"]) == 12
    assert "available_years" in data


def test_release_calendar_with_games(client: Client) -> None:
    Game.objects.create(appid=3001, name="Game A", release_date=datetime.date(2025, 10, 16))  # Jeudi
    Game.objects.create(appid=3002, name="Game B", release_date=datetime.date(2025, 10, 16))  # Jeudi
    Game.objects.create(appid=3003, name="Game C", release_date=datetime.date(2025, 5, 2))    # Vendredi

    response = client.get("/api/stats/release-calendar/?year=2025")
    assert response.status_code == 200
    data = response.json()
    assert data["selected_year"] == 2025
    assert 2025 in data["available_years"]

    # Verify daily contributions contains 2025-10-16 with count 2
    daily_dict = dict(data["daily_contributions"])
    assert daily_dict.get("2025-10-16") == 2
    assert daily_dict.get("2025-05-02") == 1

    # Verify weekday_month: jeudi (day 3), octobre (month 9) has at least 2
    cell = next((c for c in data["weekday_month"] if c[0] == 3 and c[1] == 9), None)
    assert cell is not None
    assert cell[2] == 2
