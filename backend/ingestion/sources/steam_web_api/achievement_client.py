from http import HTTPStatus
from typing import Any

from ingestion.http import ApiError
from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher
from ingestion.sources.steam_web_api.achievement import Achievement

PERCENTAGES_URL = (
    "https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
)
SCHEMA_URL = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
NO_ACHIEVEMENTS_STATUSES = frozenset({HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND})


class AchievementClient:
    """Pourcentages mondiaux des succès (sans clé) et, avec une clé, leur nom lisible."""

    def __init__(self, api_key: str = "", fetch_json: JsonFetcher | None = None) -> None:
        self._api_key = api_key
        self._fetch_json = fetch_json or cached_fetcher("steam_web_api")

    def achievements(self, appid: int) -> list[Achievement]:
        """Liste vide quand le jeu n'a pas de succès."""
        payload = self._get(PERCENTAGES_URL, {"gameid": str(appid)})
        rows = ((payload or {}).get("achievementpercentages") or {}).get("achievements") or []
        names = self._schema(appid)
        return [
            Achievement(
                name=row["name"],
                percent=float(row["percent"]),
                display_name=names.get(row["name"], {}).get("displayName", ""),
                description=names.get(row["name"], {}).get("description", ""),
            )
            for row in rows
        ]

    def _schema(self, appid: int) -> dict[str, dict[str, str]]:
        if not self._api_key:
            return {}
        payload = self._get(SCHEMA_URL, {"appid": str(appid), "key": self._api_key})
        stats = ((payload or {}).get("game") or {}).get("availableGameStats") or {}
        return {row["name"]: row for row in stats.get("achievements") or []}

    def _get(self, url: str, params: dict[str, str]) -> Any:
        try:
            return self._fetch_json(url, params)
        except ApiError as error:
            if error.status in NO_ACHIEVEMENTS_STATUSES:
                return None
            raise
