import pytest
from django.db import IntegrityError

from catalog.models import Game, GameTag, Tag
from ingestion.models import ImportRun

COUNTER_STRIKE_APPID = 730


@pytest.mark.django_db
def test_a_tag_is_linked_to_a_game_with_its_votes() -> None:
    game = Game.objects.create(appid=COUNTER_STRIKE_APPID, name="Counter-Strike 2")
    shooter = Tag.objects.create(name="FPS")

    GameTag.objects.create(game=game, tag=shooter, votes=12_000)

    assert list(game.tags.all()) == [shooter]
    assert game.game_tags.get().votes == 12_000


@pytest.mark.django_db
def test_the_same_tag_cannot_be_linked_twice() -> None:
    game = Game.objects.create(appid=COUNTER_STRIKE_APPID, name="Counter-Strike 2")
    shooter = Tag.objects.create(name="FPS")
    GameTag.objects.create(game=game, tag=shooter)

    with pytest.raises(IntegrityError):
        GameTag.objects.create(game=game, tag=shooter)


@pytest.mark.django_db
def test_an_import_run_records_its_end() -> None:
    run = ImportRun.objects.create(source="steamspy")
    assert not run.succeeded

    run.finish(rows=1_000)

    run.refresh_from_db()
    assert run.rows == 1_000
    assert run.succeeded
