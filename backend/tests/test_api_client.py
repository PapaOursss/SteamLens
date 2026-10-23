from pathlib import Path

import httpx
import pytest
import respx

from ingestion.http import ApiClient, ApiError, ResponseCache

URL = "https://steamspy.com/api.php"
PARAMS = {"request": "appdetails", "appid": 730}
BODY = {"appid": 730, "name": "Counter-Strike 2"}


class FakeTime:
    """Horloge et `sleep` factices : le test avance le temps sans attendre."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def make_client(fake_time: FakeTime, cache: ResponseCache | None = None) -> ApiClient:
    return ApiClient(
        "steamspy", cache=cache, sleep=fake_time.sleep, clock=fake_time.clock, max_attempts=3
    )


@respx.mock
def test_returns_the_json_body() -> None:
    respx.get(URL, params=PARAMS).respond(json=BODY)

    assert make_client(FakeTime()).get_json(URL, PARAMS) == BODY


@respx.mock
def test_waits_between_two_calls() -> None:
    respx.get(URL).respond(json=BODY)
    fake_time = FakeTime()
    client = make_client(fake_time)

    client.get_json(URL, {"page": 0})
    client.get_json(URL, {"page": 1})

    assert fake_time.sleeps == [1.0]


@respx.mock
def test_retries_after_a_429_then_succeeds() -> None:
    route = respx.get(URL)
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "7"}),
        httpx.Response(200, json=BODY),
    ]
    fake_time = FakeTime()

    assert make_client(fake_time).get_json(URL) == BODY
    assert 7.0 in fake_time.sleeps


@respx.mock
def test_gives_up_after_the_last_attempt() -> None:
    respx.get(URL).respond(503)

    with pytest.raises(ApiError, match="HTTP 503 après 3 essais"):
        make_client(FakeTime()).get_json(URL)


@respx.mock
def test_does_not_retry_a_404() -> None:
    route = respx.get(URL).respond(404)

    with pytest.raises(ApiError, match="HTTP 404"):
        make_client(FakeTime()).get_json(URL)
    assert route.call_count == 1


@respx.mock
def test_a_cached_response_skips_the_network(tmp_path: Path) -> None:
    route = respx.get(URL).respond(json=BODY)
    fake_time = FakeTime()
    cache = ResponseCache(tmp_path, time_to_live_seconds=60, clock=fake_time.clock)
    client = make_client(fake_time, cache)

    client.get_json(URL, PARAMS)
    second = client.get_json(URL, PARAMS)

    assert second == BODY
    assert route.call_count == 1


def test_an_expired_cache_entry_is_ignored(tmp_path: Path) -> None:
    fake_time = FakeTime()
    cache = ResponseCache(tmp_path, time_to_live_seconds=60, clock=fake_time.clock)
    cache.set(URL, PARAMS, BODY)

    fake_time.now += 61

    assert cache.get(URL, PARAMS) is None


def test_the_api_key_is_never_written_to_disk(tmp_path: Path) -> None:
    cache = ResponseCache(tmp_path, time_to_live_seconds=60)

    cache.set(URL, {"key": "secret-api-key"}, BODY)

    for cached_file in tmp_path.iterdir():
        assert "secret-api-key" not in cached_file.name
        assert "secret-api-key" not in cached_file.read_text()
