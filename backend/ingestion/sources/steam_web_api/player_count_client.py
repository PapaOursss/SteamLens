from collections.abc import Callable, Iterable, Iterator
from datetime import UTC, datetime
from http import HTTPStatus

from ingestion.http import ApiError
from ingestion.sources.json_fetcher import JsonFetcher, live_fetcher
from ingestion.sources.steam_web_api.player_count import PlayerCount

API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
RESULT_OK = 1


def utc_now() -> datetime:
    return datetime.now(UTC)


class PlayerCountClient:
    """Photographie les joueurs connectés (`GetNumberOfCurrentPlayers`, clé facultative).

    Steam ne garde aucun historique : c'est en répétant ces photos qu'on construit le nôtre.
    Jamais de cache ici, le chiffre doit être celui de l'instant.
    """

    def __init__(
        self,
        fetch_json: JsonFetcher | None = None,
        now: Callable[[], datetime] = utc_now,
        api_key: str = "",
    ) -> None:
        self._fetch_json = fetch_json or live_fetcher("steam_web_api")
        self._now = now
        self._api_key = api_key

    def current_players(self, appid: int) -> PlayerCount | None:
        """None quand Steam ne compte pas ce jeu (appid inconnu, outil, bande-son…)."""
        params = {"appid": str(appid)}
        if self._api_key:
            params["key"] = self._api_key
        try:
            payload = self._fetch_json(API_URL, params)
        except ApiError as error:
            if error.status == HTTPStatus.NOT_FOUND:
                return None
            raise
        response = payload.get("response") or {}
        if response.get("result") != RESULT_OK or "player_count" not in response:
            return None
        return PlayerCount(
            appid=appid,
            player_count=int(response["player_count"]),
            counted_at=self._now(),
        )

    def snapshot(self, appids: Iterable[int]) -> Iterator[PlayerCount]:
        for appid in appids:
            player_count = self.current_players(appid)
            if player_count is not None:
                yield player_count
