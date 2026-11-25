from typing import Any

from pricing.cheapshark_client import CheapsharkClient, store_directory

STEAM_STORE_ID = "1"


def _format_offer(item: dict[str, Any], store: dict[str, str], store_id: str) -> dict[str, Any]:
    deal_id = item.get("dealID", "")
    return {
        "store_id": store_id,
        "store_name": store["name"],
        "store_icon": store["icon"],
        "deal_id": deal_id,
        "price": float(item.get("salePrice", 0)),
        "regular_price": float(item.get("normalPrice", 0)),
        "cut_percent": round(float(item.get("savings", 0))),
        "is_steam": store_id == STEAM_STORE_ID,
        "redirect_url": f"https://www.cheapshark.com/redirect?dealID={deal_id}",
    }


def get_game_store_comparison(appid: int, client: CheapsharkClient | None = None) -> dict[str, Any]:
    """Compare le prix Steam aux autres magasins ; à prix égal, Steam compte comme le moins cher."""
    cheapshark = client or CheapsharkClient()
    stores = store_directory(cheapshark)
    deals: list[dict[str, Any]] = []
    for item in cheapshark.fetch_deals_for_game(appid):
        if not isinstance(item, dict):
            continue
        store_id = str(item.get("storeID", ""))
        store = stores.get(store_id, {"name": f"Magasin {store_id}", "icon": ""})
        deals.append(_format_offer(item, store, store_id))

    deals.sort(key=lambda deal: (deal["price"], not deal["is_steam"]))
    cheapest = deals[0] if deals else None
    steam_price = next((deal["price"] for deal in deals if deal["is_steam"]), None)
    return {
        "appid": appid,
        "steam_price": steam_price,
        "cheapest_price": cheapest["price"] if cheapest else None,
        "cheapest_store": cheapest["store_name"] if cheapest else None,
        "steam_is_cheapest": bool(cheapest and cheapest["is_steam"]),
        "stores_count": len(deals),
        "deals": deals,
    }
