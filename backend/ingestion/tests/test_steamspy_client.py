import json
import unittest
from pathlib import Path
from typing import Any

from ingestion.sources.steamspy import SteamSpyClient
from ingestion.sources.steamspy.request_pacer import RequestPacer

FIXTURES = Path(__file__).parent / "fixtures" / "steamspy"


class FakeFetcher:
    """Renvoie des réponses préparées et garde la trace des paramètres demandés."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, str]] = []

    def __call__(self, url: str, params: dict[str, str]) -> Any:
        self.calls.append(params)
        return self._responses.pop(0)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def top_100_extract() -> dict:
    return json.loads((FIXTURES / "top100in2weeks_extract.json").read_text(encoding="utf-8"))


class SteamSpyClientTests(unittest.TestCase):
    def test_iter_all_games_stops_on_empty_page(self) -> None:
        fetcher = FakeFetcher([top_100_extract(), top_100_extract(), {}])
        client = SteamSpyClient(fetch_json=fetcher, all_pages_pacer=RequestPacer(0))
        games = list(client.iter_all_games())
        self.assertEqual(len(games), 6)
        self.assertEqual([call["page"] for call in fetcher.calls], ["0", "1", "2"])

    def test_app_details_sends_appid(self) -> None:
        details = json.loads((FIXTURES / "appdetails_730.json").read_text(encoding="utf-8"))
        fetcher = FakeFetcher([details])
        game = SteamSpyClient(fetch_json=fetcher, default_pacer=RequestPacer(0)).app_details(730)
        self.assertEqual(fetcher.calls, [{"request": "appdetails", "appid": "730"}])
        self.assertEqual(game.name, "Counter-Strike: Global Offensive")

    def test_tops_use_their_request_names(self) -> None:
        fetcher = FakeFetcher([top_100_extract(), top_100_extract()])
        client = SteamSpyClient(fetch_json=fetcher, default_pacer=RequestPacer(0))
        client.top_100_in_2_weeks()
        client.top_100_forever()
        requests = [call["request"] for call in fetcher.calls]
        self.assertEqual(requests, ["top100in2weeks", "top100forever"])


class RequestPacerTests(unittest.TestCase):
    def test_waits_only_the_remaining_time(self) -> None:
        clock = FakeClock()
        pacer = RequestPacer(60, clock=clock, sleep=clock.sleep)
        pacer.wait()
        clock.now += 15
        pacer.wait()
        self.assertEqual(clock.sleeps, [45])

    def test_no_wait_when_interval_already_elapsed(self) -> None:
        clock = FakeClock()
        pacer = RequestPacer(1, clock=clock, sleep=clock.sleep)
        pacer.wait()
        clock.now += 5
        pacer.wait()
        self.assertEqual(clock.sleeps, [])


if __name__ == "__main__":
    unittest.main()
