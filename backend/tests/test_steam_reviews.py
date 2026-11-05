import datetime

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from catalog.models import Game, ReviewSummary, ReviewWeek
from catalog.review_bombing import find_bombings
from ingestion.management.commands import import_reviews
from ingestion.sources.steam_reviews import SteamReviewsClient, count_by_week
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

SUMMARY = "steam_reviews/summary_413150_french"
RECENT_PAGE = "steam_reviews/recent_413150_page"
NOVEMBER_WEEK = datetime.date(2026, 11, 2)
OCTOBER_WEEK = datetime.date(2026, 10, 26)


def test_counts_reads_the_query_summary() -> None:
    fetcher = FakeFetcher([load_fixture(SUMMARY)])
    counts = SteamReviewsClient(fetch_json=fetcher).counts(413150, "french")
    assert (counts.positive, counts.negative) == (12873, 154)
    assert fetcher.calls[0]["language"] == "french"
    assert fetcher.calls[0]["num_per_page"] == "0"


def test_counts_is_none_when_steam_fails() -> None:
    fetcher = FakeFetcher([{"success": 2}])
    assert SteamReviewsClient(fetch_json=fetcher).counts(413150, "french") is None


def test_recent_reviews_stop_on_a_short_page() -> None:
    fetcher = FakeFetcher([load_fixture(RECENT_PAGE)])
    reviews = list(SteamReviewsClient(fetch_json=fetcher).recent_reviews(413150, max_pages=3))
    assert [review.voted_up for review in reviews] == [True, False, True]
    assert len(fetcher.calls) == 1
    assert fetcher.calls[0]["cursor"] == "*"


def test_reviews_are_counted_by_monday() -> None:
    fetcher = FakeFetcher([load_fixture(RECENT_PAGE)])
    weeks = count_by_week(SteamReviewsClient(fetch_json=fetcher).recent_reviews(413150))
    assert (weeks[NOVEMBER_WEEK].positive, weeks[NOVEMBER_WEEK].negative) == (1, 1)
    assert (weeks[OCTOBER_WEEK].positive, weeks[OCTOBER_WEEK].negative) == (1, 0)


@pytest.mark.django_db
def test_import_keeps_only_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)
    summaries = [load_fixture(SUMMARY)] + [{"success": 1, "query_summary": {}}] * 10
    fetcher = FakeFetcher([*summaries, load_fixture(RECENT_PAGE)])
    monkeypatch.setattr(
        import_reviews, "build_client", lambda: SteamReviewsClient(fetch_json=fetcher)
    )

    call_command("import_reviews", limit=1)

    summary = ReviewSummary.objects.get()
    assert (summary.language, summary.positive) == ("english", 12873)
    assert ReviewWeek.objects.get(week_start=NOVEMBER_WEEK).negative == 1
    stored = [str(value) for row in ReviewWeek.objects.values() for value in row.values()]
    assert not any("76561198" in value for value in stored)


def weeks_with_shares(*shares: float) -> list[ReviewWeek]:
    start = datetime.date(2026, 9, 7)
    return [
        ReviewWeek(
            week_start=start + datetime.timedelta(weeks=index),
            positive=round(share * 100),
            negative=100 - round(share * 100),
        )
        for index, share in enumerate(shares)
    ]


def test_a_sudden_drop_is_a_bombing() -> None:
    bombings = find_bombings(weeks_with_shares(0.9, 0.92, 0.88, 0.9, 0.4, 0.85))
    assert [bombing.week_start for bombing in bombings] == [datetime.date(2026, 10, 5)]
    assert bombings[0].drop == pytest.approx(0.5)


def test_a_slow_decline_is_not_a_bombing() -> None:
    assert find_bombings(weeks_with_shares(0.9, 0.85, 0.8, 0.75, 0.7, 0.65)) == []


@pytest.mark.django_db
def test_game_reviews_endpoint() -> None:
    game = Game.objects.create(appid=413150, name="Stardew Valley")
    ReviewSummary.objects.create(
        game=game, language="french", positive=90, negative=10, date=datetime.date(2026, 11, 5)
    )
    for week in weeks_with_shares(0.9, 0.9, 0.9, 0.9, 0.3):
        week.game = game
        week.save()

    data = APIClient().get(reverse("stats-game-reviews", args=[413150])).json()

    assert data["languages"][0]["positive_share"] == 0.9
    assert len(data["weeks"]) == 5
    assert len(data["bombings"]) == 1
    bombed = APIClient().get(reverse("stats-review-bombings")).json()
    assert bombed[0]["name"] == "Stardew Valley"
