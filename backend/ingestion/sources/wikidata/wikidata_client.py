from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import batched
from typing import Any

from ingestion.http import ApiClient, ResponseCache
from ingestion.sources.wikidata.studio_query import COUNTRY_PATHS, studio_query

SPARQL_URL = "https://query.wikidata.org/sparql"
# Une requête par paquet d'appids : assez petite pour rester loin de la limite de 60 secondes.
APPIDS_PER_QUERY = 200

type SparqlGetter = Callable[[str], Any]


@dataclass(frozen=True)
class StudioCountry:
    iso2: str
    iso3: str
    name: str


@dataclass(frozen=True)
class GameStudio:
    appid: int
    wikidata_id: str
    name: str
    country: StudioCountry | None


def build_wikidata_client() -> "WikidataClient":
    """Client réel, réponses en cache disque (le pays d'un studio change rarement)."""
    api = ApiClient("wikidata", cache=ResponseCache.for_source("wikidata"))
    return WikidataClient(
        lambda query: api.get_json(SPARQL_URL, {"query": query, "format": "json"})
    )


class WikidataClient:
    def __init__(self, get: SparqlGetter) -> None:
        self._get = get

    def studios(self, appids: Iterable[int]) -> list[GameStudio]:
        """Un studio par jeu et par développeur ; le pays le plus sûr quand il y en a plusieurs."""
        found: dict[tuple[int, str], GameStudio] = {}
        for batch in batched(appids, APPIDS_PER_QUERY):
            body = self._get(studio_query(batch))
            for binding in body.get("results", {}).get("bindings", []):
                studio = _parse(binding)
                if studio is None:
                    continue
                key = (studio.appid, studio.wikidata_id)
                if key not in found or (found[key].country is None and studio.country):
                    found[key] = studio
        return list(found.values())


def _parse(binding: dict[str, Any]) -> GameStudio | None:
    appid = _value(binding, "appid")
    name = _value(binding, "developerLabel")
    wikidata_id = _value(binding, "developer").rsplit("/", 1)[-1]
    # Sans libellé, le service renvoie l'identifiant (« Q123 ») : pas un nom de studio.
    if not appid.isdigit() or not name or name == wikidata_id:
        return None
    return GameStudio(int(appid), wikidata_id, name.strip(), _country(binding))


def _country(binding: dict[str, Any]) -> StudioCountry | None:
    for key, _ in COUNTRY_PATHS:
        iso2 = _value(binding, f"{key}_iso2")
        iso3 = _value(binding, f"{key}_iso3")
        if len(iso2) == 2 and len(iso3) == 3:
            return StudioCountry(iso2.upper(), iso3.upper(), _value(binding, f"{key}Label"))
    return None


def _value(binding: dict[str, Any], name: str) -> str:
    return str((binding.get(name) or {}).get("value") or "")
