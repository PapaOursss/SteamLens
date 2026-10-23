import unittest
from datetime import date
from decimal import Decimal

from ingestion.sources.request_pacer import RequestPacer
from ingestion.sources.steam_store import SteamStoreClient, StorePrice
from ingestion.sources.steam_store.release_date import parse_release_date
from ingestion.tests.fakes import FakeFetcher, load_fixture

ELDEN_RING_APPID = 1245620
DETAILS_FIXTURE = "steam_store/appdetails_1245620_fr.json"
PRICES_FIXTURE = "steam_store/price_overview_br.json"


def client_returning(*responses: object) -> tuple[SteamStoreClient, FakeFetcher]:
    fetcher = FakeFetcher(list(responses))
    return SteamStoreClient(fetch_json=fetcher, pacer=RequestPacer(0)), fetcher


class AppDetailsTests(unittest.TestCase):
    def test_reads_the_game_sheet(self) -> None:
        client, fetcher = client_returning(load_fixture(DETAILS_FIXTURE))
        details = client.app_details(ELDEN_RING_APPID)
        self.assertEqual(fetcher.calls[0]["appids"], str(ELDEN_RING_APPID))
        self.assertEqual(details.name, "ELDEN RING")
        self.assertEqual(details.genres, ["Action", "RPG"])
        self.assertEqual(details.platforms, ["windows"])
        self.assertEqual(details.metacritic_score, 94)
        self.assertEqual(len(details.screenshot_urls), 2)
        self.assertIn("GTX 1060", details.minimum_requirements_html)
        self.assertEqual(details.price.currency, "EUR")

    def test_unknown_game_gives_none(self) -> None:
        client, _ = client_returning({"999999999": {"success": False}})
        self.assertIsNone(client.app_details(999999999))


class PricesTests(unittest.TestCase):
    def test_skips_free_games(self) -> None:
        client, fetcher = client_returning(load_fixture(PRICES_FIXTURE))
        prices = client.prices([1172470, 730, ELDEN_RING_APPID], "br")
        self.assertEqual(fetcher.calls[0]["filters"], "price_overview")
        self.assertEqual(fetcher.calls[0]["appids"], "1172470,730,1245620")
        expected = StorePrice(
            appid=ELDEN_RING_APPID,
            country_code="BR",
            currency="BRL",
            initial_amount=Decimal("274.50"),
            final_amount=Decimal("274.50"),
            discount_percent=0,
        )
        self.assertEqual(prices, [expected])

    def test_splits_appids_into_batches(self) -> None:
        client, fetcher = client_returning({}, {}, {})
        client.prices(range(120), "us")
        self.assertEqual([len(call["appids"].split(",")) for call in fetcher.calls], [50, 50, 20])

    def test_asks_each_country_once(self) -> None:
        client, fetcher = client_returning({}, {})
        list(client.prices_in_every_country([730], ["fr", "jp"]))
        self.assertEqual([call["cc"] for call in fetcher.calls], ["fr", "jp"])


class ReleaseDateTests(unittest.TestCase):
    def test_reads_english_dates(self) -> None:
        self.assertEqual(parse_release_date("24 Feb, 2022"), date(2022, 2, 24))
        self.assertEqual(parse_release_date("Feb 24, 2022"), date(2022, 2, 24))

    def test_vague_or_localized_dates_give_none(self) -> None:
        for text in ("Coming soon", "Q3 2027", "24 févr. 2022", ""):
            with self.subTest(text=text):
                self.assertIsNone(parse_release_date(text))


if __name__ == "__main__":
    unittest.main()
