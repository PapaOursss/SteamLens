from typing import Any

from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher

GIVEAWAYS_URL = "https://www.gamerpower.com/api/giveaways"
QUERY = {"platform": "steam", "type": "game"}
NO_END_DATE = "N/A"


class GamerPowerClient:
    """Jeux Steam offerts en ce moment (GamerPower, sans clé)."""

    def __init__(self, fetch_json: JsonFetcher | None = None) -> None:
        self._fetch_json = fetch_json or cached_fetcher("gamerpower")

    def active_giveaways(self) -> list[dict[str, Any]]:
        """Sans offre en cours, l'API répond un objet au lieu d'une liste."""
        body = self._fetch_json(GIVEAWAYS_URL, QUERY)
        offers = body if isinstance(body, list) else []
        return [self._read(offer) for offer in offers if offer.get("status") == "Active"]

    def _read(self, offer: dict[str, Any]) -> dict[str, Any]:
        end_date = offer.get("end_date") or NO_END_DATE
        return {
            "id": offer["id"],
            "title": offer["title"],
            "image": offer.get("thumbnail", ""),
            "url": offer["open_giveaway_url"],
            "end_date": None if end_date == NO_END_DATE else end_date,
        }
