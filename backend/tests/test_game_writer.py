import datetime

import pytest

from catalog.models import Game, GamePlaytime, GameTag, ReviewSummary
from ingestion.writing import GameRecord, GameWriter

OLD = datetime.date(2019, 6, 1)
NEW = datetime.date(2026, 10, 1)


def stardew(**overrides: object) -> GameRecord:
    values: dict = {
        "appid": 413150,
        "name": "Stardew Valley",
        "fields": {"owners_mid": 35_000_000, "supported_languages": ["English", "French"]},
        "genres": ["Indie", "RPG"],
        "tag_votes": {"Farming Sim": 7935},
        "developers": ["ConcernedApe"],
        "positive_reviews": 900,
        "negative_reviews": 100,
        "median_playtime_minutes": 3000,
    }
    return GameRecord(**(values | overrides))


@pytest.mark.django_db
def test_creates_the_game_and_its_links() -> None:
    GameWriter(NEW).save([stardew()])

    game = Game.objects.get(appid=413150)
    assert game.owners_mid == 35_000_000
    assert game.data_date == NEW
    assert sorted(game.genres.values_list("name", flat=True)) == ["Indie", "RPG"]
    assert game.developers.get().name == "ConcernedApe"
    assert GameTag.objects.get(game=game).votes == 7935
    assert GamePlaytime.objects.get(game=game).median_playtime_minutes == 3000
    assert ReviewSummary.objects.get(game=game, language="all", date=NEW).positive == 900


@pytest.mark.django_db
def test_running_twice_creates_no_duplicate() -> None:
    GameWriter(NEW).save([stardew()])
    GameWriter(NEW).save([stardew(tag_votes={"Farming Sim": 8000})])

    assert Game.objects.count() == 1
    assert GameTag.objects.get().votes == 8000
    assert ReviewSummary.objects.count() == 1


@pytest.mark.django_db
def test_older_data_only_fills_the_gaps() -> None:
    GameWriter(NEW).save([stardew()])
    older = stardew(name="Stardew (2019)", fields={"owners_mid": 1, "release_date": OLD})

    GameWriter(OLD).save([older])

    game = Game.objects.get()
    assert game.name == "Stardew Valley"
    assert game.owners_mid == 35_000_000
    assert game.release_date == OLD
    assert game.data_date == NEW


@pytest.mark.django_db
def test_tags_without_votes_keep_the_known_votes() -> None:
    GameWriter(NEW).save([stardew()])

    GameWriter(NEW).save([stardew(tag_votes={"Farming Sim": 0, "Cozy": 0})])

    votes = dict(GameTag.objects.values_list("tag__name", "votes"))
    assert votes == {"Farming Sim": 7935, "Cozy": 0}


@pytest.mark.django_db
def test_blank_names_are_ignored() -> None:
    GameWriter(NEW).save([stardew(genres=["", "  "], developers=[" "])])

    game = Game.objects.get()
    assert not game.genres.exists()
    assert not game.developers.exists()
