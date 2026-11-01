from collections.abc import Callable
from typing import Any

from ingestion.http import ApiClient, ResponseCache

JsonFetcher = Callable[[str, dict[str, str]], Any]


def cached_fetcher(source: str) -> JsonFetcher:
    """GET JSON par le client partagé : cache disque, débit de la source, reprises.

    Les clients des sources reçoivent un `JsonFetcher` : les tests leur passent des fixtures.
    """
    return ApiClient(source, cache=ResponseCache.for_source(source)).get_json
