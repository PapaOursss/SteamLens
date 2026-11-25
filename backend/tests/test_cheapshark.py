from unittest.mock import MagicMock

from pricing.cheapshark_client import CheapsharkClient
from pricing.cheapshark_compare import get_game_store_comparison
from pricing.cheapshark_deals import get_top_deals


def fake_stores():
    return [
        {
            "storeID": "1",
            "storeName": "Steam",
            "isActive": 1,
            "images": {"icon": "/img/stores/icons/0.png"},
        },
        {
            "storeID": "2",
            "storeName": "GamersGate",
            "isActive": 1,
            "images": {"icon": "/img/stores/icons/1.png"},
        },
        {
            "storeID": "3",
            "storeName": "GreenManGaming",
            "isActive": 1,
            "images": {"icon": "/img/stores/icons/2.png"},
        },
    ]


def test_cheapshark_compare_detects_cheapest_store():
    client = MagicMock(spec=CheapsharkClient)
    client.fetch_stores.return_value = fake_stores()
    client.fetch_deals_for_game.return_value = [
        {"storeID": "1", "salePrice": "19.99", "normalPrice": "19.99", "savings": "0", "dealID": "d1"},
        {"storeID": "2", "salePrice": "9.99", "normalPrice": "19.99", "savings": "50", "dealID": "d2"},
    ]

    result = get_game_store_comparison(570, client=client)

    assert result["appid"] == 570
    assert result["steam_price"] == 19.99
    assert result["cheapest_price"] == 9.99
    assert result["cheapest_store"] == "GamersGate"
    assert result["steam_is_cheapest"] is False
    assert len(result["deals"]) == 2


def test_cheapshark_compare_when_steam_is_cheapest():
    client = MagicMock(spec=CheapsharkClient)
    client.fetch_stores.return_value = fake_stores()
    client.fetch_deals_for_game.return_value = [
        {"storeID": "1", "salePrice": "4.99", "normalPrice": "19.99", "savings": "75", "dealID": "d1"},
        {"storeID": "3", "salePrice": "14.99", "normalPrice": "19.99", "savings": "25", "dealID": "d3"},
    ]

    result = get_game_store_comparison(730, client=client)

    assert result["steam_is_cheapest"] is True
    assert result["cheapest_store"] == "Steam"


def test_cheapshark_top_deals_formats_deal_attributes():
    client = MagicMock(spec=CheapsharkClient)
    client.fetch_stores.return_value = fake_stores()
    client.fetch_top_deals.return_value = [
        {
            "title": "Celeste",
            "dealID": "deal123",
            "storeID": "1",
            "salePrice": "4.99",
            "normalPrice": "19.99",
            "savings": "75.038",
            "steamRatingPercent": "97",
            "steamRatingText": "Overwhelmingly Positive",
            "dealRating": "9.8",
            "steamAppID": "504230",
            "thumb": "https://example.com/thumb.jpg",
        }
    ]

    deals = get_top_deals(client=client)

    assert len(deals) == 1
    deal = deals[0]
    assert deal["title"] == "Celeste"
    assert deal["sale_price"] == 4.99
    assert deal["normal_price"] == 19.99
    assert deal["cut_percent"] == 75
    assert deal["steam_rating_percent"] == 97
    assert deal["steam_appid"] == 504230
    assert deal["store_name"] == "Steam"
    assert "deal123" in deal["redirect_url"]
