export interface GenreStat {
  name: string
  games: number
}

export interface TagStat {
  name: string
  games: number
  votes: number
}

export interface TopPlayedGame {
  appid: number
  name: string
  header_image: string
  players: number
  taken_at: string
}

export interface PlayerCountSnapshotItem {
  taken_at: string
  players: number
  source: string
}

export interface PricePointItem {
  date: string
  country: string
  currency: string
  price: number
  price_eur: number
  discount_percent: number
  source: string
}

export type WorldMapData = Record<string, number>
