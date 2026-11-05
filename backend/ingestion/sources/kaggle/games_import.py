from collections.abc import Callable
from pathlib import Path

from django.utils import timezone

from ingestion.http import ApiError
from ingestion.import_tracking import ImportReport
from ingestion.sources.kaggle.cleaning import latest_date
from ingestion.sources.kaggle.kaggle_download import KaggleDownloadError, dataset_file
from ingestion.sources.kaggle.kaggle_game import KaggleGame
from ingestion.sources.kaggle.usd_price import save_usd_prices
from ingestion.writing import GameWriter
from pricing.euro_converter import EuroConverter

MISSING_KEYS = "Clés Kaggle absentes : passer --file ou remplir backend/.env."

type GamesReader = Callable[[Path, int | None], list[KaggleGame]]


def build_converter() -> EuroConverter:
    try:
        return EuroConverter.from_frankfurter()
    except (ApiError, KeyError):
        return EuroConverter({})


def resolve_dataset_file(
    report: ImportReport, dataset: str, filename: str, given: Path | None
) -> Path | None:
    """Le fichier passé par `--file`, sinon celui du dataset (téléchargé au besoin)."""
    if given is not None:
        return given
    try:
        path = dataset_file(dataset, filename)
    except KaggleDownloadError as error:
        report.add_error(str(error))
        return None
    if path is None:
        report.add_error(MISSING_KEYS)
    return path


def import_games(
    report: ImportReport, source: str, path: Path, read: GamesReader, limit: int | None
) -> None:
    """Écrit les jeux d'un CSV Kaggle, datés par la sortie la plus récente qu'il contient."""
    games = read(path, limit)
    data_date = latest_date(
        [game.record.fields.get("release_date") for game in games], timezone.localdate()
    )
    report.rows = GameWriter(data_date).save(game.record for game in games)
    prices = [game.price for game in games if game.price is not None]
    report.rows += save_usd_prices(prices, source, data_date, build_converter())
