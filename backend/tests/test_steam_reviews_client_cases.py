import datetime

import pytest

from ingestion.sources.steam_reviews import (
    RecentReview,
    SteamReviewsClient,
    count_by_week,
    week_start,
)
from ingestion.sources.steam_reviews.steam_reviews_client import REVIEWS_PER_PAGE
from tests.fake_fetcher import FakeFetcher

TIMESTAMP = 1793865600  # jeudi 2026-11-05 08:00 UTC


def review(steamid: str = "1", voted_up: bool = True, timestamp: int = TIMESTAMP) -> dict:
    return {"author": {"steamid": steamid}, "timestamp_created": timestamp, "voted_up": voted_up}


def page(count: int, cursor: str) -> dict:
    return {"success": 1, "reviews": [review(str(n)) for n in range(count)], "cursor": cursor}


def recent(*pages: object, max_pages: int = 5) -> tuple[list[RecentReview], FakeFetcher]:
    fetcher = FakeFetcher(list(pages))
    reviews = list(SteamReviewsClient(fetch_json=fetcher).recent_reviews(1, max_pages=max_pages))
    return reviews, fetcher


def test_full_pages_follow_the_cursor() -> None:
    reviews, fetcher = recent(page(REVIEWS_PER_PAGE, "A"), page(3, "B"))
    assert len(reviews) == REVIEWS_PER_PAGE + 3
    assert [call["cursor"] for call in fetcher.calls] == ["*", "A"]


def test_pagination_stops_at_max_pages() -> None:
    reviews, fetcher = recent(page(REVIEWS_PER_PAGE, "A"), page(REVIEWS_PER_PAGE, "B"), max_pages=2)
    assert len(reviews) == 2 * REVIEWS_PER_PAGE
    assert len(fetcher.calls) == 2


def test_pagination_stops_when_the_cursor_does_not_move() -> None:
    _, fetcher = recent(page(REVIEWS_PER_PAGE, "*"))
    assert len(fetcher.calls) == 1


def test_pagination_stops_without_cursor() -> None:
    _, fetcher = recent({"success": 1, "reviews": [review()] * REVIEWS_PER_PAGE})
    assert len(fetcher.calls) == 1


def test_a_failed_page_gives_no_review() -> None:
    reviews, _ = recent({"success": 2})
    assert reviews == []


def test_a_review_without_author_keeps_an_empty_id() -> None:
    reviews, _ = recent({"success": 1, "reviews": [{"timestamp_created": TIMESTAMP}]})
    assert reviews[0].author_steamid == ""
    assert reviews[0].voted_up is False


def test_dates_are_utc() -> None:
    reviews, _ = recent(page(1, "A"))
    assert reviews[0].created_at == datetime.datetime(2026, 11, 5, 8, tzinfo=datetime.UTC)


def test_every_request_asks_json_for_all_purchases() -> None:
    _, fetcher = recent(page(1, "A"))
    assert fetcher.calls[0]["json"] == "1"
    assert fetcher.calls[0]["purchase_type"] == "all"
    assert fetcher.calls[0]["language"] == "all"
    assert fetcher.calls[0]["num_per_page"] == str(REVIEWS_PER_PAGE)


def test_counts_without_summary_are_zero() -> None:
    fetcher = FakeFetcher([{"success": 1}])
    counts = SteamReviewsClient(fetch_json=fetcher).counts(1, "german")
    assert (counts.positive, counts.negative, counts.language) == (0, 0, "german")


def test_counts_of_a_non_json_answer_is_none() -> None:
    fetcher = FakeFetcher(["<html>Welcome to Steam</html>"])
    assert SteamReviewsClient(fetch_json=fetcher).counts(1, "french") is None


@pytest.mark.parametrize(
    ("day", "monday"),
    [
        (datetime.date(2026, 11, 2), datetime.date(2026, 11, 2)),
        (datetime.date(2026, 11, 8), datetime.date(2026, 11, 2)),
        (datetime.date(2026, 11, 9), datetime.date(2026, 11, 9)),
        (datetime.date(2027, 1, 1), datetime.date(2026, 12, 28)),
    ],
)
def test_week_start_is_the_monday(day: datetime.date, monday: datetime.date) -> None:
    assert week_start(day) == monday


def test_count_by_week_of_nothing_is_empty() -> None:
    assert count_by_week([]) == {}


def test_count_by_week_separates_weeks() -> None:
    sunday = datetime.datetime(2026, 11, 8, 23, 59, tzinfo=datetime.UTC)
    monday = sunday + datetime.timedelta(minutes=1)
    weeks = count_by_week([RecentReview(sunday, True, "1"), RecentReview(monday, False, "2")])
    assert sorted(weeks) == [datetime.date(2026, 11, 2), datetime.date(2026, 11, 9)]
