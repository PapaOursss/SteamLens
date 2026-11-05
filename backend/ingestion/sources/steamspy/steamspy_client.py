import logging
from collections.abc import Iterator
from typing import Any

from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher
from ingestion.sources.steamspy.steamspy_game import SteamSpyGame

logger = logging.getLogger(__name__)

API_URL = "https://steamspy.com/api.php"


class SteamSpyClient:
    """Lit l'API SteamSpy (sans clé) en respectant ses limites : 1 appel/s, `all` 1 appel/min.

    Les deux débits viennent de `source_limits` (`steamspy`, `steamspy_all`) ; les tests
    passent des fixtures à la place des deux `JsonFetcher`.
    """

    def __init__(
        self,
        fetch_json: JsonFetcher | None = None,
        fetch_all_pages_json: JsonFetcher | None = None,
    ) -> None:
        self._fetch_json = fetch_json or cached_fetcher("steamspy")
        self._fetch_all_pages_json = fetch_all_pages_json or cached_fetcher("steamspy_all")

    def all_games_page(self, page: int) -> list[SteamSpyGame]:
        """Une page de 1 000 jeux ; une page vide signifie qu'on a tout lu."""
        payload = self._fetch_all_pages_json(API_URL, {"request": "all", "page": str(page)})
        return _games_from_mapping(payload)

    def iter_all_games(self, first_page: int = 0) -> Iterator[SteamSpyGame]:
        page = first_page
        while games := self.all_games_page(page):
            yield from games
            page += 1

    def app_details(self, appid: int) -> SteamSpyGame:
        payload = self._fetch_json(API_URL, {"request": "appdetails", "appid": str(appid)})
        return SteamSpyGame.from_payload(payload)

    def top_100_in_2_weeks(self) -> list[SteamSpyGame]:
        return _games_from_mapping(self._fetch_json(API_URL, {"request": "top100in2weeks"}))

    def top_100_forever(self) -> list[SteamSpyGame]:
        return _games_from_mapping(self._fetch_json(API_URL, {"request": "top100forever"}))


def _games_from_mapping(payload: dict[str, dict[str, Any]] | list) -> list[SteamSpyGame]:
    """SteamSpy indexe ses listes par appid, dans l'ordre du classement.

    Un jeu illisible (fourchette de propriétaires inconnue…) est sauté, pas toute la page.
    """
    if not isinstance(payload, dict):
        return []
    games = []
    for entry in payload.values():
        try:
            games.append(SteamSpyGame.from_payload(entry))
        except (KeyError, ValueError) as error:
            logger.warning("Jeu SteamSpy illisible sauté : %s", error)
    return games
