import datetime
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.achievement_curve import (
    abandon_curve,
    biggest_drop,
    completion_rate,
    is_ending,
    median_percent,
)
from catalog.models import AchievementStat, Game
from catalog.views.achievements import RANKING_SIZE
from ingestion.http import ApiError
from ingestion.management.commands import import_achievements
from ingestion.models import ImportRun
from ingestion.sources.steam_web_api import AchievementClient
from tests.fake_fetcher import FakeFetcher

DAY = datetime.date(2026, 11, 5)


def stat(name: str, percent: str, display: str = "", description: str = "") -> AchievementStat:
    return AchievementStat(name=name, display_name=display, description=description,
                           percent=Decimal(percent), date=DAY)  # fmt: skip


def percentages(*rows: tuple[str, object]) -> dict:
    achievements = [{"name": name, "percent": percent} for name, percent in rows]
    return {"achievementpercentages": {"achievements": achievements}}


@pytest.mark.parametrize(
    ("achievement", "expected"),
    [
        (stat("ACH_ENDING", "1"), True),
        (stat("a1", "1", display="The End"), True),
        (stat("a2", "1", description="Finish the game on any difficulty"), True),
        (stat("a3", "1", description="Terminer le jeu"), True),
        (stat("a4", "1", description="Watch the CREDITS roll"), True),
        (stat("a5", "1", display="Pending"), False),
        (stat("a7", "1", description="Defending the base for 10 waves"), False),
        (stat("a8", "1", description="Unlock the true ending."), True),
        (stat("a6", "1", display="First blood", description="Kill an enemy"), False),
    ],
)
def test_ending_keywords(achievement: AchievementStat, expected: bool) -> None:
    assert is_ending(achievement) is expected


def test_completion_rate_takes_the_most_common_ending() -> None:
    achievements = [stat("good", "8", description="Good ending"),
                    stat("bad", "3", description="Bad ending"), stat("x", "90")]  # fmt: skip
    assert completion_rate(achievements) == 8.0


def test_completion_rate_without_ending_is_none() -> None:
    assert completion_rate([stat("x", "50")]) is None
    assert completion_rate([]) is None


def test_curve_is_sorted_and_ranked() -> None:
    curve = abandon_curve([stat("b", "10"), stat("a", "60", display="Début"), stat("c", "35")])
    assert [(step["rank"], step["name"], step["percent"]) for step in curve] == [
        (1, "Début", 60.0), (2, "c", 35.0), (3, "b", 10.0)
    ]  # fmt: skip


def test_biggest_drop_needs_two_achievements() -> None:
    assert biggest_drop([]) is None
    assert biggest_drop(abandon_curve([stat("a", "10")])) is None


def test_biggest_drop_is_rounded() -> None:
    curve = abandon_curve([stat("a", "50.55"), stat("b", "10.10"), stat("c", "5")])
    assert biggest_drop(curve) == {"from_achievement": "a", "to_achievement": "b", "drop": 40.45}


def test_median_percent() -> None:
    assert median_percent([stat("a", "10"), stat("b", "20"), stat("c", "90")]) == 20.0
    assert median_percent([stat("a", "10"), stat("b", "21")]) == 15.5


def test_numeric_percentages_are_read_too() -> None:
    fetcher = FakeFetcher([percentages(("a", 12.5))])
    assert AchievementClient(fetch_json=fetcher).achievements(1)[0].percent == 12.5


def test_a_missing_list_gives_nothing() -> None:
    assert AchievementClient(fetch_json=FakeFetcher([{}])).achievements(1) == []


def test_not_found_gives_nothing() -> None:
    fetcher = FakeFetcher([ApiError("steam_web_api", "url", "HTTP 404", 404)])
    assert AchievementClient(fetch_json=fetcher).achievements(1) == []


def test_server_errors_are_raised() -> None:
    fetcher = FakeFetcher([ApiError("steam_web_api", "url", "HTTP 500", 500)])
    with pytest.raises(ApiError):
        AchievementClient(fetch_json=fetcher).achievements(1)


def test_a_forbidden_schema_keeps_the_raw_names() -> None:
    fetcher = FakeFetcher([percentages(("a", "5")), ApiError("s", "u", "HTTP 403", 403)])
    achievement = AchievementClient("key", fetch_json=fetcher).achievements(1)[0]
    assert (achievement.name, achievement.display_name) == ("a", "")


def test_the_schema_request_carries_the_key() -> None:
    fetcher = FakeFetcher([percentages(("a", "5")), {"game": {}}])
    AchievementClient("key", fetch_json=fetcher).achievements(42)
    assert fetcher.calls[1] == {"appid": "42", "key": "key"}


@pytest.mark.django_db
@override_settings(API_KEYS={"STEAM_API_KEY": ""})
def test_import_traces_errors_and_goes_on(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=1, name="A", owners_mid=20)
    Game.objects.create(appid=2, name="B", owners_mid=10)
    fetcher = FakeFetcher(
        [ApiError("steam_web_api", "u", "HTTP 500", 500), percentages(("x", "3"))]
    )
    monkeypatch.setattr(
        import_achievements, "build_client", lambda: AchievementClient(fetch_json=fetcher)
    )
    call_command("import_achievements")
    assert list(AchievementStat.objects.values_list("game_id", flat=True)) == [2]
    assert "HTTP 500" in ImportRun.objects.get(source="steam_achievements").errors


@pytest.mark.django_db
def test_build_client_uses_the_steam_key() -> None:
    with override_settings(API_KEYS={"STEAM_API_KEY": "abc"}):
        assert import_achievements.build_client()._api_key == "abc"


def test_unknown_game_gives_404(db: None) -> None:
    assert APIClient().get(reverse("stats-game-achievements", args=[1])).status_code == 404


def test_game_without_achievements(db: None) -> None:
    Game.objects.create(appid=1, name="Vide")
    data = APIClient().get(reverse("stats-game-achievements", args=[1])).json()
    assert (data["curve"], data["completion_rate"], data["biggest_drop"]) == ([], None, None)


def test_ranking_is_limited(db: None) -> None:
    for appid in range(1, RANKING_SIZE + 6):
        game = Game.objects.create(appid=appid, name=f"Jeu {appid}")
        AchievementStat.objects.create(game=game, name="end", description="The end",
                                       percent=Decimal(appid), date=DAY)  # fmt: skip
    ranking = APIClient().get(reverse("stats-least-finished")).json()
    assert len(ranking) == RANKING_SIZE
    assert ranking[0]["completion_rate"] == 1.0
    assert ranking[0]["achievements"] == 1


def test_ranking_without_data_is_empty(db: None) -> None:
    assert APIClient().get(reverse("stats-least-finished")).json() == []
