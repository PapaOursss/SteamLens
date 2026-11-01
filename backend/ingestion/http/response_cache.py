import hashlib
import json
import time
from collections.abc import Callable, Mapping
from pathlib import Path

from django.conf import settings

from ingestion.http.json_types import JsonValue, QueryParams


class ResponseCache:
    """Cache disque des réponses JSON : une requête déjà faite ne repart pas sur le réseau.

    Un fichier par requête, nommé par l'empreinte de l'URL et des paramètres : la clé d'API
    éventuelle n'est donc jamais écrite en clair sur le disque.
    """

    def __init__(
        self,
        directory: Path,
        time_to_live_seconds: float,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.directory = directory
        self.time_to_live_seconds = time_to_live_seconds
        self.clock = clock

    @classmethod
    def for_source(cls, source: str) -> "ResponseCache":
        """Cache réglé par `settings.HTTP_CACHE_DIR` et `HTTP_CACHE_TTL_SECONDS`."""
        return cls(settings.HTTP_CACHE_DIR / source, settings.HTTP_CACHE_TTL_SECONDS)

    def get(self, url: str, params: QueryParams) -> JsonValue | None:
        path = self._path(url, params)
        if not path.exists():
            return None
        entry = json.loads(path.read_text(encoding="utf-8"))
        if self.clock() - entry["fetched_at"] > self.time_to_live_seconds:
            return None
        body: JsonValue = entry["body"]
        return body

    def set(self, url: str, params: QueryParams, body: JsonValue) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        entry = {"fetched_at": self.clock(), "body": body}
        self._path(url, params).write_text(json.dumps(entry), encoding="utf-8")

    def _path(self, url: str, params: QueryParams) -> Path:
        return self.directory / f"{request_fingerprint(url, params)}.json"


def request_fingerprint(url: str, params: Mapping[str, str | int]) -> str:
    canonical = json.dumps([url, sorted((key, str(value)) for key, value in params.items())])
    return hashlib.sha256(canonical.encode()).hexdigest()
