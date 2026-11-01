from dataclasses import dataclass

from ingestion.sources.kaggle.usd_price import UsdPrice
from ingestion.writing import GameRecord


@dataclass
class KaggleGame:
    """Une ligne de dataset Kaggle : le jeu à écrire et son prix américain s'il y en a un."""

    record: GameRecord
    price: UsdPrice | None = None
