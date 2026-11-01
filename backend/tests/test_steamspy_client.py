import unittest

from ingestion.sources.steamspy import SteamSpyClient
from tests.fake_fetcher import FakeFetcher
from tests.fixture_files import load_fixture

TOP_100_EXTRACT = "steamspy/top100in2weeks_extract"


class SteamSpyClientTests(unittest.TestCase):
    def test_iter_all_games_stops_on_empty_page(self) -> None:
        page = load_fixture(TOP_100_EXTRACT)
        fetcher = FakeFetcher([page, page, {}])
        client = SteamSpyClient(fetch_json=fetcher, fetch_all_pages_json=fetcher)
        games = list(client.iter_all_games())
        self.assertEqual(len(games), 6)
        self.assertEqual([call["page"] for call in fetcher.calls], ["0", "1", "2"])

    def test_app_details_sends_appid(self) -> None:
        fetcher = FakeFetcher([load_fixture("steamspy/appdetails_730")])
        game = SteamSpyClient(fetch_json=fetcher, fetch_all_pages_json=fetcher).app_details(730)
        self.assertEqual(fetcher.calls, [{"request": "appdetails", "appid": "730"}])
        self.assertEqual(game.name, "Counter-Strike: Global Offensive")

    def test_tops_use_their_request_names(self) -> None:
        fetcher = FakeFetcher([load_fixture(TOP_100_EXTRACT), load_fixture(TOP_100_EXTRACT)])
        client = SteamSpyClient(fetch_json=fetcher, fetch_all_pages_json=fetcher)
        client.top_100_in_2_weeks()
        client.top_100_forever()
        requests = [call["request"] for call in fetcher.calls]
        self.assertEqual(requests, ["top100in2weeks", "top100forever"])
