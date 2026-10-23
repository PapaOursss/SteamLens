import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from ingestion.sources.resource_not_found import ResourceNotFound

REQUEST_TIMEOUT_SECONDS = 30

JsonFetcher = Callable[[str, dict[str, str]], Any]


def fetch_json_over_http(url: str, params: dict[str, str]) -> Any:
    """Appel GET minimal, en attendant le client HTTP partagé (cache, reprises).

    Lève ResourceNotFound sur un 404, que les sources traitent comme « absent ».
    """
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(full_url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == HTTPStatus.NOT_FOUND:
            raise ResourceNotFound(full_url) from error
        raise
