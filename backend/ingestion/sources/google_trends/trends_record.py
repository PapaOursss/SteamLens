from datetime import date
from typing import NamedTuple


class TrendsRecord(NamedTuple):
    """Point d'intérêt Google Trends pour un jeu et un pays à une date donnée."""

    appid: int
    iso2: str
    date: date
    interest: int
