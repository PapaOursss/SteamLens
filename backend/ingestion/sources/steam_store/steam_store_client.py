from collections.abc import Iterable, Iterator
from itertools import batched
from typing import Any

from ingestion.sources.json_fetcher import JsonFetcher, fetch_json_over_http
from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.steam_store.price_countries import PRICE_COUNTRY_CODES
from ingestion.sources.steam_store.store_app_details import StoreAppDetails
from ingestion.sources.steam_store.store_price import StorePrice

API_URL = "https://store.steampowered.com/api/appdetails"
SECONDS_PER_REQUEST = 1.5
APPIDS_PER_PRICE_REQUEST = 50
DEFAULT_COUNTRY_CODE = "fr"
DEFAULT_LANGUAGE = "english"


class SteamStoreClient:
    """Lit l'API non documentée du Store (sans clé), à ~200 appels / 5 min au plus.

    La fiche complète ne se demande qu'un jeu à la fois ; les prix (`price_overview`) se
    demandent par paquets de jeux, un pays par appel.
    """

    def __init__(
        self,
        fetch_json: JsonFetcher = fetch_json_over_http,
        pacer: RequestPacer | None = None,
    ) -> None:
        self._fetch_json = fetch_json
        self._pacer = pacer or RequestPacer(SECONDS_PER_REQUEST)

    def app_details(
        self,
        appid: int,
        country_code: str = DEFAULT_COUNTRY_CODE,
        language: str = DEFAULT_LANGUAGE,
    ) -> StoreAppDetails | None:
        """None quand le Store ne connaît pas le jeu (retiré, région bloquée…)."""
        payload = self._request(appids=str(appid), cc=country_code, l=language)
        data = _successful_data(payload, appid)
        return StoreAppDetails.from_data(data, country_code) if data else None

    def prices(self, appids: Iterable[int], country_code: str) -> list[StorePrice]:
        """Les jeux gratuits ou sans prix dans ce pays sont absents du résultat."""
        found: list[StorePrice] = []
        for batch in batched(appids, APPIDS_PER_PRICE_REQUEST):
            payload = self._request(
                appids=",".join(str(appid) for appid in batch),
                cc=country_code,
                filters="price_overview",
            )
            found.extend(_prices_from_payload(payload, batch, country_code))
        return found

    def prices_in_every_country(
        self, appids: Iterable[int], country_codes: Iterable[str] = PRICE_COUNTRY_CODES
    ) -> Iterator[StorePrice]:
        appid_list = list(appids)
        for country_code in country_codes:
            yield from self.prices(appid_list, country_code)

    def _request(self, **params: str) -> Any:
        self._pacer.wait()
        return self._fetch_json(API_URL, params)


def _successful_data(payload: dict[str, Any] | None, appid: int) -> dict[str, Any] | None:
    """Le Store renvoie `data: []` (et non un objet) pour un jeu gratuit filtré sur le prix."""
    entry = (payload or {}).get(str(appid)) or {}
    data = entry.get("data")
    if not entry.get("success") or not isinstance(data, dict):
        return None
    return data


def _prices_from_payload(
    payload: dict[str, Any], appids: Iterable[int], country_code: str
) -> Iterator[StorePrice]:
    for appid in appids:
        data = _successful_data(payload, appid)
        if data and data.get("price_overview"):
            yield StorePrice.from_price_overview(appid, country_code, data["price_overview"])
