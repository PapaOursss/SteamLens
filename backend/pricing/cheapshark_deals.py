from typing import Any

from pricing.cheapshark_client import CheapsharkClient, store_directory

TOP_DEALS_COUNT = 30
# CheapShark liste chaque offre : un même jeu revient d'un magasin à l'autre. On en lit plus
# pour garder assez de jeux différents une fois les doublons retirés.
FETCHED_DEALS = 60


def _format_deal(item: dict[str, Any], store: dict[str, str]) -> dict[str, Any]:
    steam_appid = item.get("steamAppID")
    deal_id = item.get("dealID", "")
    return {
        "title": item.get("title", "Sans titre"),
        "deal_id": deal_id,
        "store_name": store["name"],
        "store_icon": store["icon"],
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


def get_top_deals(
    count: int = TOP_DEALS_COUNT, client: CheapsharkClient | None = None
) -> list[dict[str, Any]]:
    """Les meilleures promotions sur des jeux bien notés, une seule (la mieux classée) par jeu."""
    cheapshark = client or CheapsharkClient()
    stores = store_directory(cheapshark)
    seen_games: set[str] = set()
    deals: list[dict[str, Any]] = []
    for item in cheapshark.fetch_top_deals(page_size=FETCHED_DEALS):
        if not isinstance(item, dict):
            continue
        game_key = str(item.get("gameID") or item.get("title", "")).lower()
        if game_key in seen_games:
            continue
        seen_games.add(game_key)
        store_id = str(item.get("storeID", ""))
        store = stores.get(store_id, {"name": f"Magasin {store_id}", "icon": ""})
        deals.append(_format_deal(item, store))
        if len(deals) == count:
            break
    return deals
