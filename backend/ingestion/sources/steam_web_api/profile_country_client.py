from collections import Counter
from collections.abc import Iterable
from itertools import batched

from ingestion.sources.json_fetcher import JsonFetcher, live_fetcher

API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
STEAMIDS_PER_REQUEST = 100
NO_COUNTRY = ""


class ProfileCountryClient:
    """Pays déclaré (`loccountrycode`, facultatif) des profils publics, par lots de 100 (T-37).

    Ne renvoie que des comptes par pays : ni SteamID ni pseudo ne sortent d'ici, et rien
    n'est mis en cache sur le disque.
    """

    def __init__(self, api_key: str, fetch_json: JsonFetcher | None = None) -> None:
        self._api_key = api_key
        self._fetch_json = fetch_json or live_fetcher("steam_web_api")

    def count_countries(self, steamids: Iterable[str]) -> Counter[str]:
        """Profils comptés par code ISO-2 ; `NO_COUNTRY` pour ceux sans pays déclaré."""
        countries: Counter[str] = Counter()
        for batch in batched(steamids, STEAMIDS_PER_REQUEST):
            params = {"key": self._api_key, "steamids": ",".join(batch)}
            players = (self._fetch_json(API_URL, params).get("response") or {}).get("players")
            for player in players or []:
                countries[str(player.get("loccountrycode") or NO_COUNTRY).upper()] += 1
        return countries
