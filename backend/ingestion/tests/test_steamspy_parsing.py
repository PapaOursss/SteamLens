import unittest
from decimal import Decimal

from ingestion.sources.steamspy import OwnersRange, SteamSpyGame
from ingestion.tests.fakes import load_fixture


class OwnersRangeTests(unittest.TestCase):
    def test_parses_min_max_and_midpoint(self) -> None:
        owners = OwnersRange.from_text("1,000,000 .. 2,000,000")
        self.assertEqual(owners, OwnersRange(minimum=1_000_000, maximum=2_000_000))
        self.assertEqual(owners.midpoint, 1_500_000)

    def test_accepts_zero_lower_bound(self) -> None:
        self.assertEqual(OwnersRange.from_text("0 .. 20,000").midpoint, 10_000)

    def test_rejects_unreadable_text(self) -> None:
        for text in ("", "1,000", "a .. b", "2,000 .. 1,000"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                OwnersRange.from_text(text)


class SteamSpyGameTests(unittest.TestCase):
    def test_parses_app_details(self) -> None:
        game = SteamSpyGame.from_payload(load_fixture("steamspy/appdetails_730.json"))
        self.assertEqual(game.appid, 730)
        self.assertEqual(game.owners.minimum, 100_000_000)
        self.assertEqual(game.price_usd, Decimal(0))
        self.assertEqual(game.genres, ["Action", "Free To Play"])
        self.assertIn("Portuguese - Brazil", game.languages)
        self.assertEqual(game.tag_votes["FPS"], 91172)

    def test_converts_cents_to_dollars(self) -> None:
        payload = load_fixture("steamspy/appdetails_730.json") | {"price": "999", "initialprice": ""}
        game = SteamSpyGame.from_payload(payload)
        self.assertEqual(game.price_usd, Decimal("9.99"))
        self.assertIsNone(game.initial_price_usd)

    def test_empty_tag_list_becomes_empty_dict(self) -> None:
        payload = load_fixture("steamspy/appdetails_730.json") | {"tags": []}
        self.assertEqual(SteamSpyGame.from_payload(payload).tag_votes, {})

    def test_list_entries_have_no_tags(self) -> None:
        payloads = load_fixture("steamspy/top100in2weeks_extract.json").values()
        games = [SteamSpyGame.from_payload(payload) for payload in payloads]
        self.assertEqual([game.appid for game in games], [730, 1172470, 578080])
        self.assertTrue(all(game.tag_votes == {} for game in games))


if __name__ == "__main__":
    unittest.main()
