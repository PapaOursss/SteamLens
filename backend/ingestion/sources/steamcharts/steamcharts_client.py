from datetime import UTC, datetime
from http import HTTPStatus

from ingestion.http import ApiError
from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher
from ingestion.sources.steam_web_api import PlayerCount

CHART_URL = "https://steamcharts.com/app/{appid}/chart-data.json"
MILLISECONDS_PER_SECOND = 1000


class SteamChartsClient:
    """Historique des joueurs connectés tenu par SteamCharts depuis 2012 (sans clé).

    Un point par mois dans le passé, puis un par heure sur les derniers jours : de quoi
    tracer les courbes avant que nos propres photos (`snapshot_players`) existent.
    """

    def __init__(self, fetch_json: JsonFetcher | None = None) -> None:
        self._fetch_json = fetch_json or cached_fetcher("steamcharts")

    def history(self, appid: int) -> list[PlayerCount]:
        """Liste vide quand SteamCharts ne suit pas ce jeu."""
        try:
            points = self._fetch_json(CHART_URL.format(appid=appid), {})
        except ApiError as error:
            if error.status == HTTPStatus.NOT_FOUND:
                return []
            raise
        return [
            PlayerCount(
                appid=appid,
                player_count=int(players),
                counted_at=datetime.fromtimestamp(timestamp / MILLISECONDS_PER_SECOND, UTC),
            )
            for timestamp, players in points or []
            if players is not None
        ]
