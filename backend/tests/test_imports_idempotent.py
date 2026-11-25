"""Relancer un import ne duplique rien (T-49) ; les autres commandes le vérifient chez elles."""

from decimal import Decimal

import pytest
from django.core.management import call_command, get_commands
from django.test import override_settings

from catalog.models import Game, GamePlaytime, GameTag
from geography.models import Country, GoogleTrendsInterest
from ingestion.management.commands import import_rawg
from ingestion.scheduling import SCHEDULE
from ingestion.sources.kaggle import games_import
from ingestion.sources.rawg import RawgClient
from players.models import PlayerCountSnapshot
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint
from tests.fixture_files import FIXTURES_DIR
from tests.test_import_rawg import FakeRawgFetcher

# T-21 n'est pas encore écrit : le planificateur saute la commande.
NOT_WRITTEN_YET = {"snapshot_twitch"}


def counts(*models: type) -> list[int]:
    return [model.objects.count() for model in models]


def run_twice(models: tuple[type, ...], command: str, *args: str, **options: object) -> None:
    call_command(command, *args, **options)
    first = counts(*models)
    call_command(command, *args, **options)
    assert all(first), f"{command} n'a rien écrit"
    assert counts(*models) == first


@pytest.mark.django_db
def test_fronkongames(monkeypatch: pytest.MonkeyPatch) -> None:
    converter = EuroConverter({"USD": Decimal("1.25")})
    monkeypatch.setattr(games_import, "build_converter", lambda: converter)
    path = FIXTURES_DIR / "kaggle" / "fronkongames_games_extract.csv"

    run_twice((Game, GamePlaytime, GameTag, PricePoint), "import_kaggle_fronkongames", file=path)


@pytest.mark.django_db
def test_player_history_csv() -> None:
    path = FIXTURES_DIR / "steamcharts" / "sample_player_history.csv"

    run_twice((Game, PlayerCountSnapshot), "import_player_history_csv", str(path))


@pytest.mark.django_db
def test_google_trends_csv() -> None:
    Game.objects.create(appid=892970, name="Valheim")
    Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    path = FIXTURES_DIR / "google_trends" / "sample_trends.csv"

    run_twice(
        (GoogleTrendsInterest,),
        "import_google_trends",
        "--csv", str(path), "--appid", "892970", "--date", "2026-11-05",
    )  # fmt: skip


@pytest.mark.django_db
@override_settings(API_KEYS={"RAWG_API_KEY": "fake-key"})
def test_rawg(monkeypatch: pytest.MonkeyPatch) -> None:
    Game.objects.create(appid=620, name="Portal 2", owners_mid=1)
    client = RawgClient("fake-key", fetch_json=FakeRawgFetcher())
    monkeypatch.setattr(import_rawg, "RawgClient", lambda key: client)

    run_twice((Game, GamePlaytime, GameTag), "import_rawg", appid=620)


def test_every_scheduled_command_exists() -> None:
    missing = {entry.command for entry in SCHEDULE} - set(get_commands())

    assert missing <= NOT_WRITTEN_YET
