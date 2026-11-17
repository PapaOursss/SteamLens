import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from geography.models import RegionalSales
from ingestion.models import ImportRun
from tests.fixture_files import FIXTURES_DIR

VGSALES = FIXTURES_DIR / "kaggle" / "vgsales_extract.csv"


@pytest.mark.django_db
def test_imports_one_row_per_game_and_platform() -> None:
    call_command("import_kaggle_vgsales", file=VGSALES)

    assert RegionalSales.objects.count() == 5
    pokemon = RegionalSales.objects.get(name="Pokemon Red/Pokemon Blue")
    assert (pokemon.platform, pokemon.year, pokemon.genre) == ("GB", 1996, "Role-Playing")
    assert (pokemon.na_sales, pokemon.eu_sales, pokemon.jp_sales) == (11.27, 8.89, 10.22)
    assert pokemon.other_sales == 1.0
    assert RegionalSales.objects.get(name="Call of Duty: Modern Warfare 3").genre == "Shooter"


@pytest.mark.django_db
def test_unknown_year_is_kept_empty() -> None:
    call_command("import_kaggle_vgsales", file=VGSALES)

    assert RegionalSales.objects.get(name="Madden NFL 2004").year is None


@pytest.mark.django_db
def test_running_twice_replaces_the_sales() -> None:
    call_command("import_kaggle_vgsales", file=VGSALES)
    call_command("import_kaggle_vgsales", file=VGSALES, limit=2)

    assert RegionalSales.objects.count() == 2
    assert ImportRun.objects.filter(source="kaggle_vgsales").count() == 2


@pytest.mark.django_db
def test_stats_come_from_the_import() -> None:
    call_command("import_kaggle_vgsales", file=VGSALES)

    data = APIClient().get("/api/stats/regional-sales/").json()

    assert data["is_sample"] is False
    sports = next(row for row in data["by_genre"] if row["genre"] == "Sports")
    assert (sports["na"], sports["other"]) == (45.8, 9.2)
    assert data["top_regions"]["na_favorite"] == "Sports"
    assert data["top_regions"]["jp_favorite"] == "Role-Playing"


@pytest.mark.django_db
def test_stats_say_when_they_are_a_sample() -> None:
    data = APIClient().get("/api/stats/regional-sales/").json()

    assert data["is_sample"] is True
    assert data["top_regions"]["jp_favorite"] == "Role-Playing"
