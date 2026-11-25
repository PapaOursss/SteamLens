from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher

API_URL = "https://api.rawg.io/api"
STEAM_STORE_ID = 1


class RawgClient:
    """Client pour l'API RAWG (notes, Metacritic, temps de jeu, screenshots, tags)."""

    def __init__(self, api_key: str, fetch_json: JsonFetcher | None = None) -> None:
        self._api_key = api_key
        self._fetch_json = fetch_json or cached_fetcher("rawg")

    def find_game(self, appid: int, name: str) -> dict[str, Any] | None:
        """Le jeu RAWG vendu sur Steam sous cet appid : le nom seul confond les homonymes."""
        for candidate in self._search(name):
            rawg_id = candidate.get("id")
            if rawg_id and self.game_steam_appid(rawg_id) == appid:
                return candidate
        return None

    def game_details(self, rawg_id: int) -> dict[str, Any]:
        """Détails complets d'un jeu RAWG."""
        data = self._get(f"/games/{rawg_id}")
        return data if isinstance(data, dict) else {}

    def game_steam_appid(self, rawg_id: int) -> int | None:
        """Extrait l'appid Steam depuis les magasins (stores) du jeu RAWG."""
        data = self._get(f"/games/{rawg_id}/stores")
        results = data.get("results", []) if isinstance(data, dict) else []
        for store in results:
            if store.get("store_id") == STEAM_STORE_ID or "store.steampowered.com" in store.get("url", ""):
                url = store.get("url", "")
                parts = [p for p in urlparse(url).path.split("/") if p]
                if "app" in parts:
                    idx = parts.index("app")
                    if idx + 1 < len(parts) and parts[idx + 1].isdigit():
                        return int(parts[idx + 1])
        return None

    def game_screenshots(self, rawg_id: int) -> list[str]:
        """Liste des URLs de captures d'écran du jeu."""
        data = self._get(f"/games/{rawg_id}/screenshots")
        results = data.get("results", []) if isinstance(data, dict) else []
        return [res["image"] for res in results if res.get("image")]

    def _search(self, name: str) -> list[dict[str, Any]]:
        """Résultats de la recherche, ceux qui portent exactement ce nom d'abord."""
        payload = self._get("/games", search=name, search_precise="true", page_size="5")
        results = payload.get("results", []) if isinstance(payload, dict) else []
        clean = name.strip().lower()
        return sorted(results, key=lambda result: result.get("name", "").strip().lower() != clean)

    def _get(self, path: str, **params: str) -> Any:
        return self._fetch_json(f"{API_URL}{path}", {"key": self._api_key, **params})
