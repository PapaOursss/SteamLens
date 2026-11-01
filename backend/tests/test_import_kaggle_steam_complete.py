import datetime
import io
import zipfile
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from django.core.management import call_command
from django.test import override_settings

from catalog.models import Game, GameTag, ReviewSummary
from ingestion.management.commands import import_kaggle_steam_complete
from ingestion.models import ImportRun
from ingestion.sources.kaggle import KaggleDownloadError, dataset_file
from ingestion.sources.kaggle.cleaning import latest_date, parse_date, parse_money
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint
from tests.fixture_files import FIXTURES_DIR

CSV = FIXTURES_DIR / "kaggle" / "steam_games_extract.csv"
DATA_DATE = datetime.date(2017, 12, 21)


@pytest.fixture(autouse=True)
def fixed_rates(monkeypatch: pytest.MonkeyPatch) -> None:
    converter = EuroConverter({"USD": Decimal("1.25")})
    monkeypatch.setattr(import_kaggle_steam_complete, "build_converter", lambda: converter)


@pytest.mark.django_db
def test_imports_games_tags_reviews_and_prices() -> None:
    call_command("import_kaggle_steam_complete", file=CSV)

    assert sorted(Game.objects.values_list("appid", flat=True)) == [570, 379720, 578080]
    doom = Game.objects.get(appid=379720)
    assert doom.release_date == datetime.date(2016, 5, 12)
    assert doom.data_date == DATA_DATE
    assert doom.supported_languages == ["English", "French", "Italian"]
    assert "Steam Achievements" in doom.categories
    assert list(doom.publishers.values_list("name", flat=True)) == ["Bethesda Softworks"]
    assert GameTag.objects.filter(game=doom).count() == 4
    reviews = ReviewSummary.objects.get(game=doom)
    assert (reviews.positive, reviews.negative, reviews.date) == (39146, 3404, DATA_DATE)
    price = PricePoint.objects.get(game=doom)
    assert (price.price, price.discount_percent, price.price_eur) == (
        Decimal("14.99"), 25, Decimal("11.99"),
    )  # fmt: skip
    assert Game.objects.get(appid=570).is_free
    assert ImportRun.objects.get().rows == 6


@pytest.mark.django_db
def test_running_twice_creates_no_duplicate() -> None:
    call_command("import_kaggle_steam_complete", file=CSV)
    call_command("import_kaggle_steam_complete", file=CSV)

    assert Game.objects.count() == 3
    assert PricePoint.objects.count() == 3
    assert ReviewSummary.objects.count() == 3


@pytest.mark.django_db
@override_settings(API_KEYS={"KAGGLE_USERNAME": "", "KAGGLE_KEY": ""})
def test_without_keys_or_file_the_run_says_why(tmp_path: Path) -> None:
    with override_settings(RAW_DATA_DIR=tmp_path):
        call_command("import_kaggle_steam_complete")

    assert "Clés Kaggle absentes" in ImportRun.objects.get().errors


def zipped(name: str, content: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr(name, content)
    return buffer.getvalue()


@override_settings(API_KEYS={"KAGGLE_USERNAME": "moi", "KAGGLE_KEY": "KGAT_jeton"})
def test_downloads_and_unzips_once(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []

    def answer(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=zipped("data/games.csv", b"a,b\n1,2\n"))

    transport = httpx.MockTransport(answer)
    with override_settings(RAW_DATA_DIR=tmp_path):
        first = dataset_file("owner/games", "games.csv", transport=transport)
        second = dataset_file("owner/games", "games.csv", transport=transport)

    assert first == second == tmp_path / "owner__games" / "games.csv"
    assert first.read_bytes() == b"a,b\n1,2\n"
    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer KGAT_jeton"


@override_settings(API_KEYS={"KAGGLE_USERNAME": "moi", "KAGGLE_KEY": "ancienne"})
def test_missing_file_in_archive_is_an_error(tmp_path: Path) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=zipped("autre.csv", b""))
    )
    with override_settings(RAW_DATA_DIR=tmp_path), pytest.raises(KaggleDownloadError):
        dataset_file("owner/games", "games.csv", transport=transport)


def test_cleaning_helpers() -> None:
    assert parse_date("Jan 2019") == datetime.date(2019, 1, 1)
    assert parse_date("Coming soon") is None
    assert parse_money("$1,299.99") == Decimal("1299.99")
    assert parse_money("Free to Play") == 0
    assert parse_money("Third-party") is None
    ceiling = datetime.date(2026, 11, 1)
    assert latest_date([None, datetime.date(2030, 1, 1)], ceiling) == ceiling
