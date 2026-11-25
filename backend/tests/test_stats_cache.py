from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory

from config.stats_cache import StatsCacheMiddleware

VERSION = "config.stats_cache.database_version"


@pytest.fixture(autouse=True)
def empty_cache():
    cache.clear()
    yield
    cache.clear()


def count_calls(path: str, versions: list[int | None], status: int = 200) -> int:
    calls = []

    def view(request):
        calls.append(request)
        return HttpResponse(b"{}", status=status, content_type="application/json")

    middleware = StatsCacheMiddleware(view)
    for version in versions:
        with patch(VERSION, return_value=version):
            response = middleware(RequestFactory().get(path))
            assert response["Content-Type"] == "application/json"
    return len(calls)


def test_same_database_is_served_from_cache():
    assert count_calls("/api/stats/treemap/", [1, 1]) == 1


def test_database_write_expires_cache():
    assert count_calls("/api/stats/treemap/", [1, 2]) == 2


def test_not_cached_outside_stats_on_error_or_in_memory():
    assert count_calls("/api/minigame/duel/", [1, 1]) == 2
    assert count_calls("/api/stats/treemap/", [1, 1], status=503) == 2
    assert count_calls("/api/stats/treemap/", [None, None]) == 2
