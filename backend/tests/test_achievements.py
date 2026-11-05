import datetime
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import AchievementStat, Game
from ingestion.http import ApiError
from ingestion.management.commands import import_achievements
from ingestion.sources.steam_web_api import AchievementClient
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

PERCENTAGES = "steam_web_api/achievement_percentages_413150_extract"
SCHEMA = "steam_web_api/schema_413150_extract"
DAY = datetime.date(2026, 11, 5)


def test_percentages_are_read_without_key() -> None:
    fetcher = FakeFetcher([load_fixture(PERCENTAGES)])
    achievements = AchievementClient(fetch_json=fetcher).achievements(413150)
    assert [(a.name, a.percent) for a in achievements][:2] == [("a0", 62.6), ("24", 57.6)]
    assert len(fetcher.calls) == 1


def test_the_schema_names_achievements_when_there_is_a_key() -> None:
    fetcher = FakeFetcher([load_fixture(PERCENTAGES), load_fixture(SCHEMA)])
    achievements = AchievementClient("secret", fetch_json=fetcher).achievements(413150)
    assert achievements[0].display_name == "Greenhorn"
    assert achievements[3].description == "Reach the lowest level of the mines."


def test_a_game_without_achievements_gives_an_empty_list() -> None:
    fetcher = FakeFetcher([ApiError("steam_web_api", "url", "HTTP 403", 403)])
    assert AchievementClient(fetch_json=fetcher).achievements(570) == []


@pytest.mark.django_db
def test_import_updates_each_achievement(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)
    for _ in range(2):
        fetcher = FakeFetcher([load_fixture(PERCENTAGES)])
        monkeypatch.setattr(
            import_achievements, "build_client", lambda f=fetcher: AchievementClient(fetch_json=f)
        )
        call_command("import_achievements", limit=1)

    assert AchievementStat.objects.count() == 5
    assert AchievementStat.objects.get(name="a0").percent == Decimal("62.60")


def add_achievement(game: Game, name: str, percent: str, description: str = "") -> None:
    AchievementStat.objects.create(
        game=game, name=name, percent=Decimal(percent), description=description, date=DAY
    )


@pytest.mark.django_db
def test_curve_and_least_finished_ranking() -> None:
    long_game = Game.objects.create(appid=1, name="Long jeu")
    short_game = Game.objects.create(appid=2, name="Jeu court")
    add_achievement(long_game, "start", "90")
    add_achievement(long_game, "mid", "40")
    add_achievement(long_game, "end", "12", "Finish the story")
    add_achievement(short_game, "end", "70", "See the credits")
    add_achievement(Game.objects.create(appid=3, name="Sans fin"), "start", "50")

    curve = APIClient().get(reverse("stats-game-achievements", args=[1])).json()
    ranking = APIClient().get(reverse("stats-least-finished")).json()

    assert [step["percent"] for step in curve["curve"]] == [90.0, 40.0, 12.0]
    assert curve["completion_rate"] == 12.0
    assert curve["biggest_drop"] == {
        "from_achievement": "start",
        "to_achievement": "mid",
        "drop": 50.0,
    }
    assert [game["name"] for game in ranking] == ["Long jeu", "Jeu court"]
