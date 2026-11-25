from typing import NamedTuple

from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher

API_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}"
# Un peu plus que les 266 pays et agrégats : tout tient sur une page.
QUERY = {"format": "json", "per_page": "400", "mrnev": "1"}


class IndicatorValue(NamedTuple):
    iso2: str
    year: int
    value: float


class WorldBankClient:
    """Dernière valeur non vide d'un indicateur pour chaque pays (Banque mondiale, sans clé)."""

    def __init__(self, fetch_json: JsonFetcher | None = None) -> None:
        self._fetch_json = fetch_json or cached_fetcher("world_bank")

    def latest(self, indicator: str) -> list[IndicatorValue]:
        """Une erreur de l'API arrive en 200, sans la seconde partie de la réponse."""
        body = self._fetch_json(API_URL.format(indicator=indicator), QUERY)
        rows = body[1] if isinstance(body, list) and len(body) > 1 else None
        return [
            IndicatorValue(row["country"]["id"], int(row["date"]), float(row["value"]))
            for row in rows or []
            if row["value"] is not None
        ]
