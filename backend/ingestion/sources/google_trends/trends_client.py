import json
import logging
from datetime import date
from typing import Any

from ingestion.http import ApiClient, ApiError
from ingestion.sources.google_trends.trends_record import TrendsRecord

logger = logging.getLogger(__name__)

DEFAULT_SOURCE = "google_trends"
API_EXPLORE = "https://trends.google.com/trends/api/explore"
API_GEO = "https://trends.google.com/trends/api/widgetdata/comparedgeo"
PREFIX_LEN = 5  # Retire ')]}\',\n'


class GoogleTrendsClient:
    """Client interrogeant Google Trends avec repli tolérant."""

    def __init__(self, client: ApiClient | None = None) -> None:
        self.client = client or ApiClient(DEFAULT_SOURCE)

    def interest_by_region(
        self, keyword: str, appid: int, snapshot_date: date, timeframe: str = "today 12-m"
    ) -> list[TrendsRecord]:
        """Récupère l'intérêt par région pour un mot-clé."""
        try:
            return self._fetch_interest(keyword, appid, snapshot_date, timeframe)
        except Exception as error:
            logger.warning("Échec Google Trends pour %s (%s) : %s", keyword, appid, error)
            raise

    def _fetch_interest(
        self, keyword: str, appid: int, snapshot_date: date, timeframe: str
    ) -> list[TrendsRecord]:
        req_payload = {
            "comparisonItem": [{"keyword": keyword, "geo": "", "time": timeframe}],
            "category": 0,
            "property": "",
        }
        explore_data = self._get_json_data(
            API_EXPLORE, {"hl": "en-US", "tz": "-60", "req": json.dumps(req_payload)}
        )
        geo_widget = self._find_geo_widget(explore_data)
        if not geo_widget:
            return []

        token = geo_widget.get("token")
        request_obj = geo_widget.get("request", {})
        data = self._get_json_data(
            API_GEO,
            {
                "hl": "en-US",
                "tz": "-60",
                "req": json.dumps(request_obj),
                "token": token,
            },
        )
        return self._parse_geo_payload(data, appid, snapshot_date)

    def _get_json_data(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        resp = self.client.http.get(url, params=params)
        if resp.status_code != 200:
            raise ApiError(DEFAULT_SOURCE, url, f"HTTP {resp.status_code}", resp.status_code)
        text = resp.text
        if text.startswith(")]}',"):
            text = text[PREFIX_LEN:].strip()
        return json.loads(text)

    def _find_geo_widget(self, explore_data: dict[str, Any]) -> dict[str, Any] | None:
        for widget in explore_data.get("widgets", []):
            if widget.get("id") == "GEO_MAP":
                return widget
        return None

    def _parse_geo_payload(
        self, data: dict[str, Any], appid: int, snapshot_date: date
    ) -> list[TrendsRecord]:
        rows = data.get("default", {}).get("geoMapData", [])
        records: list[TrendsRecord] = []
        for row in rows:
            geo_code = row.get("geoCode")
            values = row.get("value", [0])
            val = values[0] if values else 0
            if geo_code and len(geo_code) == 2:
                records.append(
                    TrendsRecord(
                        appid=appid,
                        iso2=geo_code,
                        date=snapshot_date,
                        interest=int(val),
                    )
                )
        return records
