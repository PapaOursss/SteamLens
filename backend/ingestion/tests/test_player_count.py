import unittest
from datetime import UTC, datetime

from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.resource_not_found import ResourceNotFound
from ingestion.sources.steam_web_api import PlayerCount, PlayerCountClient
from ingestion.tests.fakes import FakeFetcher, load_fixture

COUNTED_AT = datetime(2026, 10, 23, 14, 0, tzinfo=UTC)
KNOWN_GAME = "steam_web_api/current_players_730.json"
UNKNOWN_GAME = "steam_web_api/current_players_unknown.json"


def client_returning(*responses: object) -> tuple[PlayerCountClient, FakeFetcher]:
    fetcher = FakeFetcher(list(responses))
    client = PlayerCountClient(fetch_json=fetcher, pacer=RequestPacer(0), now=lambda: COUNTED_AT)
    return client, fetcher


class PlayerCountClientTests(unittest.TestCase):
    def test_reads_the_player_count(self) -> None:
        client, fetcher = client_returning(load_fixture(KNOWN_GAME))
        self.assertEqual(
            client.current_players(730),
            PlayerCount(appid=730, player_count=656246, counted_at=COUNTED_AT),
        )
        self.assertEqual(fetcher.calls, [{"appid": "730"}])

    def test_unknown_game_gives_none(self) -> None:
        client, _ = client_returning(load_fixture(UNKNOWN_GAME))
        self.assertIsNone(client.current_players(999999999))

    def test_not_found_answer_gives_none(self) -> None:
        client, _ = client_returning(ResourceNotFound("404"))
        self.assertIsNone(client.current_players(999999999))

    def test_snapshot_skips_games_steam_does_not_count(self) -> None:
        client, _ = client_returning(
            load_fixture(KNOWN_GAME), load_fixture(UNKNOWN_GAME), load_fixture(KNOWN_GAME)
        )
        counts = list(client.snapshot([730, 999999999, 570]))
        self.assertEqual([count.appid for count in counts], [730, 570])


if __name__ == "__main__":
    unittest.main()
