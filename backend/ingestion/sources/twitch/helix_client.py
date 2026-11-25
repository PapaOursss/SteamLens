from collections.abc import Callable, Iterator
from http import HTTPStatus
from typing import Any

from ingestion.http import ApiClient, ApiError
from ingestion.sources.igdb.twitch_token import TwitchToken

API_URL = "https://api.twitch.tv/helix/{endpoint}"
PAGE_SIZE = 100
# Les streams arrivent du plus regardé au moins regardé : 5 pages (500 streams) couvrent
# presque tous les spectateurs d'un jeu, même des plus gros.
DEFAULT_STREAM_PAGES = 5

type HelixGetter = Callable[[str, dict[str, str | int], dict[str, str]], Any]


def build_helix_client(client_id: str, client_secret: str) -> "HelixClient":
    """Client réel, sans cache : les spectateurs changent d'une heure à l'autre."""
    auth = ApiClient("twitch_auth")
    api = ApiClient("twitch")
    token = TwitchToken(
        client_id, client_secret, lambda url, params: auth.post_json(url, params=params)
    )
    return HelixClient(token, lambda url, params, headers: api.get_json(url, params, headers))


class HelixClient:
    """Interroge Twitch Helix avec le jeton d'application qui sert déjà à IGDB (T-11)."""

    def __init__(self, token: TwitchToken, get: HelixGetter) -> None:
        self._token = token
        self._get = get

    def top_games(self, limit: int) -> list[dict[str, Any]]:
        """Les catégories les plus regardées en ce moment, dans l'ordre de Twitch."""
        found: list[dict[str, Any]] = []
        for page in self._pages("games/top", {}):
            found += page
            if len(found) >= limit:
                break
        return found[:limit]

    def streams(self, game_id: str, max_pages: int = DEFAULT_STREAM_PAGES) -> list[dict[str, Any]]:
        """Les streams en direct d'une catégorie, les plus regardés d'abord."""
        found: list[dict[str, Any]] = []
        for number, page in enumerate(self._pages("streams", {"game_id": game_id}), start=1):
            found += page
            if number >= max_pages:
                break
        return found

    def _pages(self, endpoint: str, params: dict[str, str | int]) -> Iterator[list[dict[str, Any]]]:
        cursor = ""
        while True:
            query: dict[str, str | int] = {**params, "first": PAGE_SIZE}
            if cursor:
                query["after"] = cursor
            body = self._query(endpoint, query)
            rows = body.get("data") or []
            yield rows
            cursor = (body.get("pagination") or {}).get("cursor") or ""
            if not cursor or not rows:
                return

    def _query(self, endpoint: str, params: dict[str, str | int]) -> dict[str, Any]:
        try:
            return self._send(endpoint, params)
        except ApiError as error:
            if error.status != HTTPStatus.UNAUTHORIZED:
                raise
            self._token.renew()
            return self._send(endpoint, params)

    def _send(self, endpoint: str, params: dict[str, str | int]) -> dict[str, Any]:
        headers = {
            "Client-Id": self._token.client_id,
            "Authorization": f"Bearer {self._token.value()}",
        }
        return self._get(API_URL.format(endpoint=endpoint), params, headers)
