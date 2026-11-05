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
  price: string
  price_eur: string | null
  discount_percent: number
  source: string
}

export type WorldMapData = Record<string, number>

export interface TierCounts {
  platinum: number
  gold: number
  silver: number
  bronze: number
  borked: number
}

export interface ProtonStats {
  tiers: { tier: string; total: number }[]
  by_genre: { genre: string; counts: TierCounts }[]
}

export interface GenrePlaytime {
  genre: string
  median_hours: number
  sample_size: number
}

export interface BestValueGame {
  appid: number
  name: string
  header_image: string
  median_hours: number
  price_eur: number
  cost_per_hour: number
}

export interface PlaytimeStats {
  by_genre: GenrePlaytime[]
  best_value: BestValueGame[]
}

export interface HypeGame {
  appid: number
  name: string
  header_image: string
  viewers: number
  players: number
  hype_ratio: number
}

export interface HypeStats {
  watched_more: HypeGame[]
  played_in_silence: HypeGame[]
}

export interface RegionalGenreSales {
  genre: string
  na: number
  eu: number
  jp: number
}

export interface RegionalSalesStats {
  by_genre: RegionalGenreSales[]
  top_regions: {
    na_favorite: string
    eu_favorite: string
    jp_favorite: string
    notes: string
  }
}

export interface WrappedStats {
  year: number
  game_of_the_year: { appid: number; name: string; header_image: string; peak_players: number }
  trending_genre: { name: string; growth_percent: number; flagship_game: string }
  biggest_discount: { name: string; discount_percent: number; final_price_eur: number }
  biggest_flop: { name: string; reason: string }
  most_expensive_country: { country: string; premium_percent: number; reason: string }
}

export interface DuelGame {
  appid: number
  name: string
  header_image: string
  players: number
  price_eur: number
  review_score: number
}

export type DuelMetric = 'players' | 'price_eur' | 'review_score'

export interface DuelRound {
  game_a: DuelGame
  game_b: DuelGame
  metric: DuelMetric
}

export interface TreemapTag {
  id: string
  name: string
  games: number
  owners: number
  score: number
  votes?: number
}

export interface TreemapGenre {
  id: string
  name: string
  games: number
  owners: number
  score: number
  children: TreemapTag[]
}

export interface TreemapResponse {
  name: string
  children: TreemapGenre[]
}

export interface SunburstNode {
  name: string
  games: number
  owners: number
  value?: number
  children?: SunburstNode[]
}

export interface SunburstResponse {
  name: string
  children: SunburstNode[]
}
