from collections.abc import Callable
from pathlib import Path

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse

STATS_PREFIX = "/api/stats/"
CACHE_SECONDS = 600
OK = 200


def database_version() -> int | None:
    """Date de dernière écriture de la base SQLite ; rien pour une base en mémoire (tests)."""
    try:
        return Path(connection.settings_dict["NAME"]).stat().st_mtime_ns
    except OSError:
        return None


class StatsCacheMiddleware:
    """Garde les réponses des statistiques : un import écrit dans la base et périme tout."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        version = database_version()
        if request.method != "GET" or not request.path.startswith(STATS_PREFIX) or version is None:
            return self.get_response(request)
        # L'hôte et Accept changent la réponse (JSON ou page navigable de DRF).
        accept = request.headers.get("Accept", "")
        key = f"stats:{hash((version, request.get_host(), request.get_full_path(), accept))}"
        cached = cache.get(key)
        if cached is not None:
            return HttpResponse(cached[0], content_type=cached[1])
        response = self.get_response(request)
        if response.status_code == OK and not response.streaming:
            cache.set(key, (response.content, response["Content-Type"]), CACHE_SECONDS)
        return response
