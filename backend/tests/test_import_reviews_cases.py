import datetime

import pytest
from django.core.management import call_command

from catalog.models import Game, ReviewSummary, ReviewWeek
from ingestion.http import ApiError
from ingestion.management.commands import import_reviews
from ingestion.models import ImportRun
from ingestion.sources.steam_reviews import SteamReviewsClient
from ingestion.sources.steam_reviews.steam_reviews_client import REVIEWS_PER_PAGE
from tests.fake_fetcher import FakeFetcher

DAY = datetime.date(2026, 11, 5)
NEW_WEEK_TIMESTAMP = 1793865600  # 2026-11-05
OLD_WEEK_TIMESTAMP = 1793174400  # 2026-10-28
EMPTY_SUMMARY = {"success": 1, "query_summary": {"total_positive": 0, "total_negative": 0}}
LANGUAGE_COUNT = len(import_reviews.LANGUAGES)


def summary(positive: int, negative: int) -> dict:
    return {"success": 1, "query_summary": {"total_positive": positive, "total_negative": negative}}


def reviews_page(count: int, timestamp: int, cursor: str = "next") -> dict:
    rows = [
        {"author": {"steamid": "765"}, "timestamp_created": timestamp, "voted_up": n % 2 == 0}
        for n in range(count)
    ]
    return {"success": 1, "reviews": rows, "cursor": cursor}


@pytest.fixture
def stardew(db: None) -> Game:
    return Game.objects.create(appid=413150, name="Stardew Valley", owners_mid=35_000_000)


def use_responses(monkeypatch: pytest.MonkeyPatch, *responses: object) -> FakeFetcher:
    fetcher = FakeFetcher(list(responses))
    monkeypatch.setattr(
        import_reviews, "build_client", lambda: SteamReviewsClient(fetch_json=fetcher)
    )
    monkeypatch.setattr(import_reviews, "today", lambda: DAY)
    return fetcher


@pytest.mark.usefixtures("stardew")
def test_languages_without_reviews_are_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    use_responses(monkeypatch, summary(5, 1), *[EMPTY_SUMMARY] * (LANGUAGE_COUNT - 1),
                  reviews_page(1, NEW_WEEK_TIMESTAMP))  # fmt: skip
    call_command("import_reviews", limit=1)
    assert list(ReviewSummary.objects.values_list("language", flat=True)) == ["english"]


@pytest.mark.usefixtures("stardew")
def test_each_language_is_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = use_responses(monkeypatch, *[EMPTY_SUMMARY] * LANGUAGE_COUNT, reviews_page(0, 0))
    call_command("import_reviews", limit=1)
    asked = [call["language"] for call in fetcher.calls[:LANGUAGE_COUNT]]
    assert asked == list(import_reviews.LANGUAGES)


@pytest.mark.usefixtures("stardew")
def test_a_rerun_the_same_day_updates_the_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    for positive in (10, 12):
        use_responses(monkeypatch, summary(positive, 1), *[EMPTY_SUMMARY] * (LANGUAGE_COUNT - 1),
                      reviews_page(1, NEW_WEEK_TIMESTAMP))  # fmt: skip
        call_command("import_reviews", limit=1)
    assert ReviewSummary.objects.get().positive == 12
    assert ReviewWeek.objects.count() == 1


@pytest.mark.usefixtures("stardew")
def test_the_oldest_week_is_dropped_when_pages_ran_out(monkeypatch: pytest.MonkeyPatch) -> None:
    full_page = reviews_page(REVIEWS_PER_PAGE - 1, NEW_WEEK_TIMESTAMP)
    full_page["reviews"].append({"timestamp_created": OLD_WEEK_TIMESTAMP, "voted_up": True})
    use_responses(monkeypatch, *[EMPTY_SUMMARY] * LANGUAGE_COUNT, full_page)
    call_command("import_reviews", limit=1, pages=1)
    assert list(ReviewWeek.objects.values_list("week_start", flat=True)) == [
        datetime.date(2026, 11, 2)
    ]


@pytest.mark.usefixtures("stardew")
def test_every_week_is_kept_when_all_reviews_were_read(monkeypatch: pytest.MonkeyPatch) -> None:
    short_page = reviews_page(2, NEW_WEEK_TIMESTAMP)
    short_page["reviews"].append({"timestamp_created": OLD_WEEK_TIMESTAMP, "voted_up": True})
    use_responses(monkeypatch, *[EMPTY_SUMMARY] * LANGUAGE_COUNT, short_page)
    call_command("import_reviews", limit=1)
    assert ReviewWeek.objects.count() == 2


@pytest.mark.usefixtures("stardew")
def test_an_api_error_is_traced_and_the_import_goes_on(monkeypatch: pytest.MonkeyPatch) -> None:
    use_responses(monkeypatch, ApiError("steam_reviews", "url", "HTTP 500", 500))
    call_command("import_reviews", limit=1)
    run = ImportRun.objects.get(source="steam_reviews")
    assert "HTTP 500" in run.errors
    assert run.finished_at is not None


@pytest.mark.django_db
def test_without_ranked_games_the_import_says_why(monkeypatch: pytest.MonkeyPatch) -> None:
    use_responses(monkeypatch)
    call_command("import_reviews")
    assert "import_steamspy" in ImportRun.objects.get().errors


@pytest.mark.usefixtures("stardew")
def test_no_steamid_reaches_the_database(monkeypatch: pytest.MonkeyPatch) -> None:
    use_responses(monkeypatch, summary(3, 1), *[EMPTY_SUMMARY] * (LANGUAGE_COUNT - 1),
                  reviews_page(4, NEW_WEEK_TIMESTAMP))  # fmt: skip
    call_command("import_reviews", limit=1)
    for model in (ReviewSummary, ReviewWeek):
        stored = [str(value) for row in model.objects.values() for value in row.values()]
        assert not any("765" in value for value in stored)
