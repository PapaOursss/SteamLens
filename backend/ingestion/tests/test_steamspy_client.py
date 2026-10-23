import unittest

from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.steamspy import SteamSpyClient
from ingestion.tests.fakes import FakeFetcher, load_fixture

TOP_100_EXTRACT = "steamspy/top100in2weeks_extract.json"


class SteamSpyClientTests(unittest.TestCase):
    def test_iter_all_games_stops_on_empty_page(self) -> None:
        page = load_fixture(TOP_100_EXTRACT)
        fetcher = FakeFetcher([page, page, {}])
        client = SteamSpyClient(fetch_json=fetcher, all_pages_pacer=RequestPacer(0))
        games = list(client.iter_all_games())
        self.assertEqual(len(games), 6)
        self.assertEqual([call["page"] for call in fetcher.calls], ["0", "1", "2"])

    def test_app_details_sends_appid(self) -> None:
        fetcher = FakeFetcher([load_fixture("steamspy/appdetails_730.json")])
        game = SteamSpyClient(fetch_json=fetcher, default_pacer=RequestPacer(0)).app_details(730)
        self.assertEqual(fetcher.calls, [{"request": "appdetails", "appid": "730"}])
        self.assertEqual(game.name, "Counter-Strike: Global Offensive")

    def test_tops_use_their_request_names(self) -> None:
        fetcher = FakeFetcher([load_fixture(TOP_100_EXTRACT), load_fixture(TOP_100_EXTRACT)])
        client = SteamSpyClient(fetch_json=fetcher, default_pacer=RequestPacer(0))
        client.top_100_in_2_weeks()
        client.top_100_forever()
        requests = [call["request"] for call in fetcher.calls]
        self.assertEqual(requests, ["top100in2weeks", "top100forever"])


if __name__ == "__main__":
    unittest.main()
