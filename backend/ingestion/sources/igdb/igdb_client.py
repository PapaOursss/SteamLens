from collections.abc import Callable, Iterable
from http import HTTPStatus
from itertools import batched
from typing import Any

from ingestion.http import ApiClient, ApiError, ResponseCache
from ingestion.sources.igdb.twitch_token import TwitchToken

API_URL = "https://api.igdb.com/v4/{endpoint}"
STEAM_SOURCE = 1
MAX_RESULTS = 500
POPULARITY_GAMES_PER_QUERY = 50
GAME_FIELDS = (
    "name,genres.name,themes.name,game_modes.name,player_perspectives.name,"
    "involved_companies.developer,involved_companies.publisher,"
    "involved_companies.company.name,involved_companies.company.country"
)

type IgdbPoster = Callable[[str, str, dict[str, str]], Any]


def build_igdb_client(client_id: str, client_secret: str) -> "IgdbClient":
    """Client réel : jeton sans cache, requêtes IGDB en cache (débit `igdb` : 4 par seconde)."""
    auth = ApiClient("twitch_auth")
    api = ApiClient("igdb", cache=ResponseCache.for_source("igdb"))
    token = TwitchToken(
        client_id, client_secret, lambda url, params: auth.post_json(url, params=params)
    )
    return IgdbClient(token, lambda url, body, headers: api.post_json(url, body, headers=headers))


class IgdbClient:
    """Interroge IGDB en « apicalypse » : un corps texte par requête, 500 résultats au plus."""

    def __init__(self, token: TwitchToken, post: IgdbPoster) -> None:
        self._token = token
        self._post = post

    def query(self, endpoint: str, body: str) -> list[dict[str, Any]]:
        try:
            return self._send(endpoint, body)
        except ApiError as error:
            if error.status != HTTPStatus.UNAUTHORIZED:
                raise
            self._token.renew()
            return self._send(endpoint, body)

    def steam_links(self, appids: Iterable[int]) -> dict[int, int]:
        """appid Steam → id du jeu IGDB, par l'endpoint `external_games`."""
        links: dict[int, int] = {}
        for batch in batched(appids, MAX_RESULTS):
            uids = ",".join(f'"{appid}"' for appid in batch)
            rows = self.query(
                "external_games",
                f"fields game,uid; where external_game_source = {STEAM_SOURCE} & uid = ({uids});"
                f" limit {MAX_RESULTS};",
            )
            for row in rows:
                if str(row.get("uid", "")).isdigit() and row.get("game"):
                    links.setdefault(int(row["uid"]), int(row["game"]))
        return links

    def games(self, igdb_ids: Iterable[int]) -> list[dict[str, Any]]:
        found = []
        for batch in batched(igdb_ids, MAX_RESULTS):
            found += self.query(
                "games",
                f"fields {GAME_FIELDS}; where id = ({_ids(batch)}); limit {MAX_RESULTS};",
            )
        return found

    def popularity_types(self) -> dict[int, str]:
        rows = self.query("popularity_types", f"fields id,name; limit {MAX_RESULTS};")
        return {int(row["id"]): row.get("name") or f"type {row['id']}" for row in rows}

    def popularity(self, igdb_ids: Iterable[int]) -> list[dict[str, Any]]:
        found = []
        for batch in batched(igdb_ids, POPULARITY_GAMES_PER_QUERY):
            found += self.query(
                "popularity_primitives",
                f"fields game_id,popularity_type,value; where game_id = ({_ids(batch)});"
                f" limit {MAX_RESULTS};",
            )
        return found

    def _send(self, endpoint: str, body: str) -> list[dict[str, Any]]:
        headers = {
            "Client-ID": self._token.client_id,
            "Authorization": f"Bearer {self._token.value()}",
            "Accept": "application/json",
        }
        return self._post(API_URL.format(endpoint=endpoint), body, headers)


def _ids(batch: Iterable[int]) -> str:
    return ",".join(str(igdb_id) for igdb_id in batch)
