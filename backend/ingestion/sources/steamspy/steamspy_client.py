from collections.abc import Iterator
from typing import Any

from ingestion.sources.json_fetcher import JsonFetcher, fetch_json_over_http
from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.steamspy.steamspy_game import SteamSpyGame

API_URL = "https://steamspy.com/api.php"
DEFAULT_INTERVAL_SECONDS = 1.0
ALL_PAGES_INTERVAL_SECONDS = 60.0


class SteamSpyClient:
    """Lit l'API SteamSpy (sans clé) en respectant ses limites : 1 appel/s, `all` 1 appel/min.

    `fetch_json` est injectable : les tests passent des fixtures, et le client HTTP partagé
    (cache, reprises) pourra le remplacer.
    """

    def __init__(
        self,
        fetch_json: JsonFetcher = fetch_json_over_http,
        default_pacer: RequestPacer | None = None,
        all_pages_pacer: RequestPacer | None = None,
    ) -> None:
        self._fetch_json = fetch_json
        self._default_pacer = default_pacer or RequestPacer(DEFAULT_INTERVAL_SECONDS)
        self._all_pages_pacer = all_pages_pacer or RequestPacer(ALL_PAGES_INTERVAL_SECONDS)

    def all_games_page(self, page: int) -> list[SteamSpyGame]:
        """Une page de 1 000 jeux ; une page vide signifie qu'on a tout lu."""
        payload = self._request(self._all_pages_pacer, request="all", page=str(page))
        return _games_from_mapping(payload)

    def iter_all_games(self, first_page: int = 0) -> Iterator[SteamSpyGame]:
        page = first_page
        while games := self.all_games_page(page):
            yield from games
            page += 1

    def app_details(self, appid: int) -> SteamSpyGame:
        payload = self._request(self._default_pacer, request="appdetails", appid=str(appid))
        return SteamSpyGame.from_payload(payload)

    def top_100_in_2_weeks(self) -> list[SteamSpyGame]:
        return _games_from_mapping(self._request(self._default_pacer, request="top100in2weeks"))

    def top_100_forever(self) -> list[SteamSpyGame]:
        return _games_from_mapping(self._request(self._default_pacer, request="top100forever"))

    def _request(self, pacer: RequestPacer, **params: str) -> Any:
        pacer.wait()
        return self._fetch_json(API_URL, params)


def _games_from_mapping(payload: dict[str, dict[str, Any]] | list) -> list[SteamSpyGame]:
    """SteamSpy indexe ses listes par appid, dans l'ordre du classement."""
    if not isinstance(payload, dict):
        return []
    return [SteamSpyGame.from_payload(game) for game in payload.values()]
