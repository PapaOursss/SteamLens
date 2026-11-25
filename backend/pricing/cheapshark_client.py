from typing import Any

from django.conf import settings

from ingestion.http import ApiClient, ResponseCache

CHEAPSHARK_BASE_URL = "https://www.cheapshark.com/api/1.0"
# Les promos changent vite : une heure, pas la journée des autres sources.
CACHE_SECONDS = 3600


class CheapsharkClient:
    """Client HTTP pour l'API CheapShark (sans clé requise)."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api = api_client or ApiClient(
            "cheapshark",
            cache=ResponseCache(settings.HTTP_CACHE_DIR / "cheapshark", CACHE_SECONDS),
        )

    def fetch_stores(self) -> list[dict[str, Any]]:
        """Liste tous les magasins partenaires suivis par CheapShark."""
        data = self.api.get_json(f"{CHEAPSHARK_BASE_URL}/stores")
        return data if isinstance(data, list) else []

    def fetch_deals_for_game(self, appid: int) -> list[dict[str, Any]]:
        """Offres en cours pour un jeu Steam spécifique, tous magasins confondus."""
        data = self.api.get_json(f"{CHEAPSHARK_BASE_URL}/deals", params={"steamAppID": str(appid)})
        return data if isinstance(data, list) else []

    def fetch_top_deals(self, page_size: int = 30) -> list[dict[str, Any]]:
        """Plus grosses remises du moment sur des jeux bien notés (tri par Deal Rating)."""
        data = self.api.get_json(
            f"{CHEAPSHARK_BASE_URL}/deals",
            params={
                "sortBy": "Deal Rating",
                "pageSize": str(page_size),
                "steamRating": "70",
            },
        )
        return data if isinstance(data, list) else []


def store_directory(client: CheapsharkClient) -> dict[str, dict[str, str]]:
    """Nom et icône de chaque magasin, par identifiant CheapShark."""
    return {
        str(store.get("storeID")): {
            "name": store.get("storeName", "Inconnu"),
            "icon": f"https://www.cheapshark.com{store.get('images', {}).get('icon', '')}",
        }
        for store in client.fetch_stores()
        if isinstance(store, dict)
    }
