/** Promotions CheapShark ; les prix sont en dollars US, comme CheapShark les donne. */

/** Une offre d'un magasin pour un jeu (`/stats/deals/<appid>/`). */
export interface StoreOffer {
  store_id: string
  store_name: string
  store_icon: string
  deal_id: string
  price: number
  regular_price: number
  cut_percent: number
  is_steam: boolean
  redirect_url: string
}

/** Le prix d'un jeu d'un magasin à l'autre ; à prix égal, Steam compte comme le moins cher. */
export interface StoreComparison {
  appid: number
  steam_price: number | null
  cheapest_price: number | null
  cheapest_store: string | null
  steam_is_cheapest: boolean
  stores_count: number
  deals: StoreOffer[]
}

/** Une des meilleures promotions du moment, une par jeu (`/stats/deals/`). */
export interface TopDeal {
  title: string
  deal_id: string
  store_name: string
  store_icon: string
  sale_price: number
  normal_price: number
  cut_percent: number
  steam_rating_percent: number
  steam_appid: number | null
  thumb: string
  redirect_url: string
}
