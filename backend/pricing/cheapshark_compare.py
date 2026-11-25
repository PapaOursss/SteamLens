from typing import Any

from pricing.cheapshark_client import CheapsharkClient


def get_game_store_comparison(
    appid: int, client: CheapsharkClient | None = None
) -> dict[str, Any]:
    """Compare le prix Steam aux autres magasins pour un jeu donné."""
    cheapshark = client or CheapsharkClient()
    raw_stores = cheapshark.fetch_stores()
    store_map = {
        str(s.get("storeID")): {
            "name": s.get("storeName", "Inconnu"),
            "icon": f"https://www.cheapshark.com{s.get('images', {}).get('icon', '')}",
        }
        for s in raw_stores
        if isinstance(s, dict)
    }

    raw_deals = cheapshark.fetch_deals_for_game(appid)
    deals: list[dict[str, Any]] = []
    steam_price: float | None = None

    for item in raw_deals:
        if not isinstance(item, dict):
            continue
        store_id = str(item.get("storeID", ""))
        sale_price = float(item.get("salePrice", 0))
        normal_price = float(item.get("normalPrice", 0))
        savings = float(item.get("savings", 0))
        store_info = store_map.get(store_id, {"name": f"Magasin {store_id}", "icon": ""})
        is_steam = store_id == "1"

        if is_steam:
            steam_price = sale_price

        deal_data = {
            "store_id": store_id,
            "store_name": store_info["name"],
            "store_icon": store_info["icon"],
            "deal_id": item.get("dealID", ""),
            "price": sale_price,
            "regular_price": normal_price,
            "cut_percent": round(savings),
            "is_steam": is_steam,
            "redirect_url": f"https://www.cheapshark.com/redirect?dealID={item.get('dealID', '')}",
        }
        deals.append(deal_data)

    deals.sort(key=lambda d: d["price"])
    cheapest = deals[0] if deals else None
    steam_is_cheapest = bool(cheapest and cheapest["is_steam"])

    return {
        "appid": appid,
        "steam_price": steam_price,
        "cheapest_price": cheapest["price"] if cheapest else None,
        "cheapest_store": cheapest["store_name"] if cheapest else None,
        "steam_is_cheapest": steam_is_cheapest,
        "stores_count": len(deals),
        "deals": deals,
    }
