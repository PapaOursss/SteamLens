from collections.abc import Callable, Iterable, Iterator
from datetime import UTC, datetime

from ingestion.sources.json_fetcher import JsonFetcher, fetch_json_over_http
from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.resource_not_found import ResourceNotFound
from ingestion.sources.steam_web_api.player_count import PlayerCount

API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
SECONDS_PER_REQUEST = 0.5
RESULT_OK = 1


def utc_now() -> datetime:
    return datetime.now(UTC)


class PlayerCountClient:
    """Photographie les joueurs connectés (`GetNumberOfCurrentPlayers`, sans clé).

    Steam ne garde aucun historique : c'est en répétant ces photos qu'on construit le nôtre.
    """

    def __init__(
        self,
        fetch_json: JsonFetcher = fetch_json_over_http,
        pacer: RequestPacer | None = None,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self._fetch_json = fetch_json
        self._pacer = pacer or RequestPacer(SECONDS_PER_REQUEST)
        self._now = now

    def current_players(self, appid: int) -> PlayerCount | None:
        """None quand Steam ne compte pas ce jeu (appid inconnu, outil, bande-son…)."""
        self._pacer.wait()
        try:
            payload = self._fetch_json(API_URL, {"appid": str(appid)})
        except ResourceNotFound:
            return None
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
