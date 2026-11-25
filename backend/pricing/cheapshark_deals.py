from typing import Any

from pricing.cheapshark_client import CheapsharkClient


def get_top_deals(
    page_size: int = 30, client: CheapsharkClient | None = None
) -> list[dict[str, Any]]:
    """Récupère les meilleures promotions actuelles sur les jeux bien notés."""
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

    raw_deals = cheapshark.fetch_top_deals(page_size=page_size)
    results: list[dict[str, Any]] = []

    for item in raw_deals:
        if not isinstance(item, dict):
            continue
        store_id = str(item.get("storeID", ""))
        steam_appid = item.get("steamAppID")
        store_info = store_map.get(store_id, {"name": f"Magasin {store_id}", "icon": ""})
        deal_id = item.get("dealID", "")

        results.append(
            {
                "title": item.get("title", "Sans titre"),
                "deal_id": deal_id,
                "store_name": store_info["name"],
                "store_icon": store_info["icon"],
                "sale_price": float(item.get("salePrice", 0)),
                "normal_price": float(item.get("normalPrice", 0)),
                "cut_percent": round(float(item.get("savings", 0))),
                "steam_rating_percent": int(item.get("steamRatingPercent", 0) or 0),
                "steam_rating_text": item.get("steamRatingText", ""),
                "deal_rating": float(item.get("dealRating", 0)),
                "steam_appid": int(steam_appid) if steam_appid and steam_appid.isdigit() else None,
                "thumb": item.get("thumb", ""),
                "redirect_url": f"https://www.cheapshark.com/redirect?dealID={deal_id}",
            }
        )

    return results
