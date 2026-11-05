import datetime
from decimal import Decimal

import pytest
from django.core.management import call_command

from catalog.models import Game, GamePlaytime, GameTag
from ingestion.sources.kaggle import games_import
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint
from tests.fixture_files import FIXTURES_DIR

FRONKONGAMES = FIXTURES_DIR / "kaggle" / "fronkongames_games_extract.csv"
STEAM_COMPLETE = FIXTURES_DIR / "kaggle" / "steam_games_extract.csv"
DOOM = 379720


@pytest.fixture(autouse=True)
def fixed_rates(monkeypatch: pytest.MonkeyPatch) -> None:
    converter = EuroConverter({"USD": Decimal("1.25")})
    monkeypatch.setattr(games_import, "build_converter", lambda: converter)


@pytest.mark.django_db
def test_reads_the_csv_despite_its_broken_header() -> None:
    call_command("import_kaggle_fronkongames", file=FRONKONGAMES)

    wukong = Game.objects.get(appid=2358720)
    assert wukong.release_date == datetime.date(2024, 8, 19)
    assert (wukong.owners_min, wukong.owners_max, wukong.owners_mid) == (
        10_000_000, 20_000_000, 15_000_000,
    )  # fmt: skip
    assert wukong.peak_ccu == 2_415_714
    assert wukong.metacritic_score is None
    assert wukong.supported_languages == ["English", "Simplified Chinese"]
    assert wukong.data_date == datetime.date(2024, 8, 19)
    doom = Game.objects.get(appid=DOOM)
    assert doom.metacritic_score == 85
    assert doom.header_image.endswith("379720/header.jpg")
    assert doom.screenshots == ["https://shot/1.jpg", "https://shot/2.jpg"]
    assert list(doom.platforms.values_list("name", flat=True)) == ["Windows"]
    playtime = GamePlaytime.objects.get(game=doom)
    assert (playtime.average_playtime_minutes, playtime.median_playtime_minutes) == (1200, 600)
    assert PricePoint.objects.get(game=doom, source="kaggle_fronkongames").price == Decimal("19.99")


@pytest.mark.django_db
def test_the_most_recent_dataset_wins_whatever_the_order() -> None:
    call_command("import_kaggle_fronkongames", file=FRONKONGAMES)
    call_command("import_kaggle_steam_complete", file=STEAM_COMPLETE)

    doom = Game.objects.get(appid=DOOM)
    assert doom.supported_languages == ["English", "French", "German"]
    assert doom.data_date == datetime.date(2024, 8, 19)
    assert doom.short_description == "Now includes all three premium DLC packs."
    assert GameTag.objects.filter(game=doom).count() == 5
    assert PricePoint.objects.filter(game=doom).count() == 2
