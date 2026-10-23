import time
from collections.abc import Callable

import httpx

from ingestion.http.api_error import ApiError
from ingestion.http.json_types import JsonValue, QueryParams
from ingestion.http.response_cache import ResponseCache
from ingestion.http.source_limits import min_interval_for

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BACKOFF_SECONDS = 2.0
DEFAULT_TIMEOUT_SECONDS = 30.0
# Les en-têtes HTTP n'acceptent que l'ASCII.
USER_AGENT = "SteamLens/0.1 (student project; https://github.com/PapaOursss/SteamLens)"


class ApiClient:
    """Client HTTP commun à toutes les sources : cache disque, débit limité, reprises.

    Chaque commande d'import crée le sien avec le nom de sa source (voir `source_limits`) ;
    les tests lui passent un faux `sleep` et un transport `respx` : rien ne part sur le réseau.
    """

    def __init__(
        self,
        source: str,
        cache: ResponseCache | None = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.source = source
        self.cache = cache
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.min_interval_seconds = min_interval_for(source)
        self.sleep = sleep
        self.clock = clock
        self.last_request_at: float | None = None
        self.http = httpx.Client(
            timeout=DEFAULT_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )

    def get_json(self, url: str, params: QueryParams | None = None) -> JsonValue:
        """GET qui renvoie le JSON, depuis le cache si possible, sinon depuis l'API."""
        query = params or {}
        if self.cache is not None:
            cached = self.cache.get(url, query)
            if cached is not None:
                return cached
        body = self._fetch_with_retries(url, query)
        if self.cache is not None:
            self.cache.set(url, query, body)
        return body

    def close(self) -> None:
        self.http.close()

    def _fetch_with_retries(self, url: str, params: QueryParams) -> JsonValue:
        reason = ""
        for attempt in range(self.max_attempts):
            self._wait_for_rate_limit()
            try:
                response = self.http.get(url, params=params)
            except httpx.TransportError as error:
                reason = type(error).__name__
                self.sleep(self._backoff_delay(attempt, None))
                continue
            if response.status_code not in RETRYABLE_STATUSES:
                return self._parse(url, response)
            reason = f"HTTP {response.status_code}"
            self.sleep(self._backoff_delay(attempt, response.headers.get("Retry-After")))
        raise ApiError(self.source, url, f"{reason} après {self.max_attempts} essais")

    def _parse(self, url: str, response: httpx.Response) -> JsonValue:
        if response.is_error:
            raise ApiError(self.source, url, f"HTTP {response.status_code}")
        try:
            body: JsonValue = response.json()
        except ValueError as error:
            raise ApiError(self.source, url, "réponse qui n'est pas du JSON") from error
        return body

    def _wait_for_rate_limit(self) -> None:
        now = self.clock()
        if self.last_request_at is not None:
            remaining = self.last_request_at + self.min_interval_seconds - now
            if remaining > 0:
                self.sleep(remaining)
                now += remaining
        self.last_request_at = now

    def _backoff_delay(self, attempt: int, retry_after: str | None) -> float:
        if retry_after is not None and retry_after.isdigit():
            return float(retry_after)
        return self.backoff_seconds * 2**attempt
