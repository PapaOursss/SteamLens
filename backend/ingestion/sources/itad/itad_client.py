from datetime import datetime
from decimal import Decimal
from typing import Any

from ingestion.sources.itad.itad_price_change import ItadPriceChange
from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher

API_URL = "https://api.isthereanydeal.com"
LOOKUP_PATH = "/games/lookup/v1"
HISTORY_PATH = "/games/history/v2"
STEAM_SHOP_ID = "61"
DEFAULT_COUNTRY = "FR"


class ItadClient:
    """IsThereAnyDeal (clé gratuite) : lien appid → id ITAD, puis historique des prix Steam."""

    def __init__(self, api_key: str, fetch_json: JsonFetcher | None = None) -> None:
        self._api_key = api_key
        self._fetch_json = fetch_json or cached_fetcher("isthereanydeal")

    def game_id(self, appid: int) -> str | None:
        """None quand ITAD ne connaît pas le jeu."""
        payload = self._get(LOOKUP_PATH, appid=str(appid))
        if not isinstance(payload, dict) or not payload.get("found"):
            return None
        return (payload.get("game") or {}).get("id")

    def steam_history(self, itad_id: str, country: str = DEFAULT_COUNTRY) -> list[ItadPriceChange]:
        """Chaque changement de prix sur Steam, du plus ancien au plus récent."""
        payload = self._get(HISTORY_PATH, id=itad_id, country=country, shops=STEAM_SHOP_ID)
        changes = [_price_change(row) for row in payload or [] if row.get("deal")]
        return sorted(changes, key=lambda change: change.changed_at)

    def _get(self, path: str, **params: str) -> Any:
        return self._fetch_json(f"{API_URL}{path}", {"key": self._api_key, **params})


def _price_change(row: dict[str, Any]) -> ItadPriceChange:
    deal = row["deal"]
    return ItadPriceChange(
        changed_at=datetime.fromisoformat(row["timestamp"]),
        currency=deal["price"]["currency"],
        price=Decimal(str(deal["price"]["amount"])),
        regular=Decimal(str(deal["regular"]["amount"])),
        cut=int(deal.get("cut") or 0),
    )
