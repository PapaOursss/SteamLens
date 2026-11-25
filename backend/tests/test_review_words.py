import datetime

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Game, ReviewExcerpt
from catalog.review_words import review_words, top_words
from ingestion.management.commands import import_reviews
from ingestion.sources.steam_reviews import RecentReview, SteamReviewsClient, pick_excerpts
from ingestion.sources.steam_reviews.review_excerpts import EXCERPTS_PER_SIDE
from tests.fake_fetcher import FakeFetcher

NOW = datetime.datetime(2026, 11, 5, tzinfo=datetime.UTC)
STARDEW_APPID = 413150
EMPTY_SUMMARY = {"success": 1, "query_summary": {"total_positive": 0, "total_negative": 0}}


def review(text: str, language: str = "english", voted_up: bool = True) -> RecentReview:
    return RecentReview(NOW, voted_up, "76561198000000000", language=language, text=text)


def test_stopwords_short_words_and_digits_are_dropped() -> None:
    assert review_words("The farming is SO relaxing, 10/10 a must", "english") == [
        "farming",
        "relaxing",
    ]


def test_french_apostrophes_split_words() -> None:
    assert review_words("L'histoire est très belle", "french") == ["histoire", "belle"]


def test_a_word_counts_once_per_review() -> None:
    words = top_words(["cozy cozy cozy", "cozy farm"], "english")
    assert words == [{"word": "cozy", "count": 2}, {"word": "farm", "count": 1}]


def test_excerpts_keep_only_text_of_two_languages() -> None:
    picked = pick_excerpts(
        [review("  Great farm  "), review("Super", "french"), review("Отлично", "russian"),
         review("   ")]
    )  # fmt: skip
    assert [(excerpt.language, excerpt.text) for excerpt in picked] == [
        ("english", "Great farm"),
        ("french", "Super"),
    ]
    assert {excerpt.author_steamid for excerpt in picked} == {""}


def test_excerpts_are_capped_per_language_and_side() -> None:
    reviews = [review(f"text {n}") for n in range(EXCERPTS_PER_SIDE + 5)]
    reviews.append(review("bad", voted_up=False))
    picked = pick_excerpts(reviews)
    assert sum(excerpt.voted_up for excerpt in picked) == EXCERPTS_PER_SIDE
    assert len(picked) == EXCERPTS_PER_SIDE + 1


@pytest.mark.django_db
def test_import_replaces_steam_excerpts_of_the_game(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=STARDEW_APPID, name="Stardew Valley", owners_mid=35_000_000)
    ReviewExcerpt.objects.create(
        game_id=STARDEW_APPID, text="ancien", is_positive=True, language="french",
        source=import_reviews.SOURCE,
    )  # fmt: skip
    french_review = {
        "author": {"steamid": "765"},
        "timestamp_created": 1793865600,
        "voted_up": False,
        "language": "french",
        "review": "Trop de bugs",
    }
    page = {"success": 1, "cursor": "end", "reviews": [french_review]}
    fetcher = FakeFetcher([*[EMPTY_SUMMARY] * len(import_reviews.LANGUAGES), page])
    monkeypatch.setattr(
        import_reviews, "build_client", lambda: SteamReviewsClient(fetch_json=fetcher)
    )
    call_command("import_reviews", limit=1)
    assert list(ReviewExcerpt.objects.values_list("text", "is_positive", "language")) == [
        ("Trop de bugs", False, "french")
    ]


@pytest.fixture
def excerpts(db: None) -> None:
    stardew = Game.objects.create(appid=STARDEW_APPID, name="Stardew Valley")
    other = Game.objects.create(appid=70, name="Half-Life")
    for game, text, is_positive, language in (
        (stardew, "Relaxing farming", True, "english"),
        (stardew, "Relaxing music", True, "english"),
        (stardew, "Boring ending", False, "english"),
        (stardew, "Ferme reposante", True, "french"),
        (other, "Classic shooter", True, "english"),
    ):
        ReviewExcerpt.objects.create(
            game=game, text=text, is_positive=is_positive, language=language, source="test"
        )


@pytest.mark.usefixtures("excerpts")
def test_api_counts_words_of_one_game() -> None:
    response = APIClient().get("/api/stats/review-words/", {"appid": STARDEW_APPID})
    data = response.json()
    assert (data["name"], data["language"]) == ("Stardew Valley", "english")
    assert data["positive"]["reviews"] == 2
    assert data["positive"]["words"][0] == {"word": "relaxing", "count": 2}
    assert [row["word"] for row in data["negative"]["words"]] == ["boring", "ending"]


@pytest.mark.usefixtures("excerpts")
def test_api_without_game_reads_every_game_in_one_language() -> None:
    data = APIClient().get("/api/stats/review-words/", {"language": "french"}).json()
    assert data["appid"] is None
    assert data["positive"]["words"] == [
        {"word": "ferme", "count": 1},
        {"word": "reposante", "count": 1},
    ]
    assert data["negative"] == {"reviews": 0, "words": []}


@pytest.mark.django_db
def test_api_refuses_an_unknown_language() -> None:
    assert APIClient().get("/api/stats/review-words/", {"language": "klingon"}).status_code == 400
