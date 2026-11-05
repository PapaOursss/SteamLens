import datetime

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Game, Genre, ReviewExcerpt, ReviewSummary
from ingestion.sources.kaggle.steam_reviews import DATA_DATE
from tests.fixture_files import FIXTURES_DIR

REVIEWS = FIXTURES_DIR / "kaggle" / "steam_reviews_extract.csv"


@pytest.mark.django_db
def test_imports_totals_per_game() -> None:
    call_command("import_kaggle_reviews", file=REVIEWS)

    counter_strike = ReviewSummary.objects.get(game_id=10)
    assert (counter_strike.positive, counter_strike.negative) == (3, 1)
    assert (counter_strike.language, counter_strike.date) == ("english", DATA_DATE)
    assert Game.objects.get(appid=70).name == "Half-Life"
    half_life = ReviewSummary.objects.get(game_id=70)
    assert (half_life.positive, half_life.negative) == (1, 2)


@pytest.mark.django_db
def test_keeps_only_helpful_readable_excerpts() -> None:
    call_command("import_kaggle_reviews", file=REVIEWS, excerpts=5)

    texts = {
        (excerpt.game_id, excerpt.is_positive): excerpt.text
        for excerpt in ReviewExcerpt.objects.all()
    }
    assert set(texts) == {(10, True), (10, False), (70, True)}
    assert texts[(10, True)].startswith("Ruined my life")
    assert "\n" in texts[(70, True)]


@pytest.mark.django_db
def test_running_twice_replaces_the_excerpts() -> None:
    call_command("import_kaggle_reviews", file=REVIEWS)
    call_command("import_kaggle_reviews", file=REVIEWS, excerpts=1)

    assert ReviewExcerpt.objects.count() == 3
    assert ReviewSummary.objects.count() == 2


@pytest.mark.django_db
def test_sentiment_by_genre_and_release_year() -> None:
    call_command("import_kaggle_reviews", file=REVIEWS)
    shooter = Genre.objects.create(name="Action")
    for appid, year in ((10, 2000), (70, 1998)):
        game = Game.objects.get(appid=appid)
        game.release_date = datetime.date(year, 11, 1)
        game.save()
        game.genres.add(shooter)

    response = APIClient().get("/api/stats/review-sentiment/")

    assert response.status_code == 200
    assert response.json() == [
        {"genre": "Action", "year": 1998, "positive": 1, "negative": 2, "positive_share": 0.333},
        {"genre": "Action", "year": 2000, "positive": 3, "negative": 1, "positive_share": 0.75},
    ]
