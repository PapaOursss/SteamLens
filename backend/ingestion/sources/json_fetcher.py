import json
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

REQUEST_TIMEOUT_SECONDS = 30

JsonFetcher = Callable[[str, dict[str, str]], Any]


def fetch_json_over_http(url: str, params: dict[str, str]) -> Any:
    """Appel GET minimal, en attendant le client HTTP partagé (cache, reprises)."""
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(full_url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.load(response)
