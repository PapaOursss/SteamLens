import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, ReviewSummary, ReviewWeek
from catalog.review_bombing import BASELINE_WEEKS, MIN_WEEK_REVIEWS, find_bombings, positive_share

FIRST_MONDAY = datetime.date(2026, 9, 7)


def week(index: int, positive: int, negative: int) -> ReviewWeek:
    return ReviewWeek(
        week_start=FIRST_MONDAY + datetime.timedelta(weeks=index),
        positive=positive,
        negative=negative,
    )


def steady_then(positive: int, negative: int) -> list[ReviewWeek]:
    return [week(index, 90, 10) for index in range(BASELINE_WEEKS)] + [
        week(BASELINE_WEEKS, positive, negative)
    ]


def test_positive_share_of_an_empty_week_is_zero() -> None:
    assert positive_share(week(0, 0, 0)) == 0.0


def test_too_few_weeks_give_no_bombing() -> None:
    weeks = [week(index, 90, 10) for index in range(BASELINE_WEEKS - 1)] + [week(9, 0, 100)]
    assert find_bombings(weeks) == []


def test_a_drop_of_exactly_twenty_points_counts() -> None:
    assert len(find_bombings(steady_then(70, 30))) == 1


def test_a_drop_just_under_twenty_points_does_not_count() -> None:
    assert find_bombings(steady_then(71, 29)) == []


def test_a_quiet_week_is_ignored_even_if_negative() -> None:
    assert find_bombings(steady_then(0, MIN_WEEK_REVIEWS - 1)) == []


def test_quiet_weeks_do_not_enter_the_baseline() -> None:
    weeks = [week(0, 0, 5), *[week(index, 90, 10) for index in range(1, 5)], week(5, 40, 60)]
    bombing = find_bombings(weeks)[0]
    assert bombing.baseline_share == 0.9


def test_weeks_are_sorted_before_comparing() -> None:
    assert len(find_bombings(list(reversed(steady_then(10, 90))))) == 1


def test_a_rise_is_not_a_bombing() -> None:
    weeks = [week(index, 50, 50) for index in range(BASELINE_WEEKS)] + [week(4, 100, 0)]
    assert find_bombings(weeks) == []


def test_bombing_fields_are_rounded() -> None:
    weeks = steady_then(20, 10)
    weeks[-1] = week(BASELINE_WEEKS, 10, 20)
    found = find_bombings(weeks)[0]
    assert (found.positive_share, found.baseline_share, found.drop, found.reviews) == (
        0.333,
        0.9,
        0.567,
        30,
    )


@pytest.fixture
def game(db: None) -> Game:
    return Game.objects.create(appid=10, name="Jeu bombardé")


def test_unknown_game_gives_404(db: None) -> None:
    assert APIClient().get(reverse("stats-game-reviews", args=[999])).status_code == 404


def test_game_without_reviews_gives_empty_lists(game: Game) -> None:
    data = APIClient().get(reverse("stats-game-reviews", args=[game.appid])).json()
    assert (data["languages"], data["weeks"], data["bombings"]) == ([], [], [])


def test_only_the_latest_language_snapshot_is_shown(game: Game) -> None:
    for day, positive in ((datetime.date(2026, 11, 1), 1), (datetime.date(2026, 11, 5), 9)):
        ReviewSummary.objects.create(game=game, language="french", positive=positive,
                                     negative=1, date=day)  # fmt: skip
    data = APIClient().get(reverse("stats-game-reviews", args=[game.appid])).json()
    assert data["languages"] == [
        {"language": "french", "positive": 9, "negative": 1, "positive_share": 0.9}
    ]


def test_weeks_are_in_chronological_order(game: Game) -> None:
    for item in reversed(steady_then(80, 20)):
        item.game = game
        item.save()
    data = APIClient().get(reverse("stats-game-reviews", args=[game.appid])).json()
    starts = [row["week_start"] for row in data["weeks"]]
    assert starts == sorted(starts)


def test_bombings_list_is_empty_without_data(db: None) -> None:
    assert APIClient().get(reverse("stats-review-bombings")).json() == []


def test_bombings_are_sorted_by_drop(db: None) -> None:
    for appid, (positive, negative) in ((1, (60, 40)), (2, (5, 95))):
        game = Game.objects.create(appid=appid, name=f"Jeu {appid}")
        for item in steady_then(positive, negative):
            item.game = game
            item.save()
    data = APIClient().get(reverse("stats-review-bombings")).json()
    assert [row["appid"] for row in data] == [2, 1]
    assert set(data[0]) == {
        "appid",
        "name",
        "week_start",
        "positive_share",
        "baseline_share",
        "drop",
        "reviews",
    }
