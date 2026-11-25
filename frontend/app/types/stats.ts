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

export type SalesRegionKey = 'na' | 'eu' | 'jp' | 'other'

export interface RegionalGenreSales {
  genre: string
  na: number
  eu: number
  jp: number
  other: number
}

export interface RegionalSalesStats {
  by_genre: RegionalGenreSales[]
  top_regions: {
    na_favorite: string
    eu_favorite: string
    jp_favorite: string
    notes: string
  }
  is_sample: boolean
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

export interface TagNetworkNode {
  id: number
  name: string
  games: number
  community: number
}

export interface TagNetworkEdge {
  source: number
  target: number
  weight: number
}

export interface TagNetworkResponse {
  nodes: TagNetworkNode[]
  edges: TagNetworkEdge[]
}

export interface GemFinderGame {
  appid: number
  name: string
  header_image: string
  price_eur: number
  positive_percent: number
  owners: number
  genre: string
  year: number | null
  is_gem: boolean
}

export interface GemCriteria {
  max_price: number
  min_score: number
  max_owners: number
}

export interface GemFinderResponse {
  is_sample: boolean
  games: GemFinderGame[]
  genres: string[]
  years: number[]
  gem_criteria: GemCriteria
}

export interface StreamgraphEvent {
  year: number
  title: string
  description: string
}

export interface StreamgraphResponse {
  years: number[]
  genres: string[]
  series: number[][]
  events: StreamgraphEvent[]
}

export interface SankeyNode {
  name: string
}

export interface SankeyLink {
  source: string
  target: string
  value: number
}

export interface SankeyPriceReviewResponse {
  is_sample: boolean
  nodes: SankeyNode[]
  links: SankeyLink[]
  genres: string[]
  price_brackets: string[]
  review_buckets: string[]
}

export interface ReleaseCalendarResponse {
  is_sample: boolean
  weekday_month: [number, number, number][]
  daily_contributions: [string, number][]
  selected_year: number
  available_years: number[]
  days: string[]
  months: string[]
}

export interface TwitchTopCategory {
  rank: number
  name: string
  /** null : la catégorie n'est pas un jeu Steam (« Just Chatting », League of Legends…). */
  appid: number | null
  box_art_url: string
  viewers: number
  streams: number
}

export interface TwitchLanguageShare {
  /** Code ISO 639-1 de Twitch (`en`, `fr`…) ou `other`. */
  language: string
  share: number
}

export interface TwitchStats {
  is_sample: boolean
  taken_at: string | null
  top: TwitchTopCategory[]
  languages: TwitchLanguageShare[]
}

export interface StudioGenreScore {
  genre: string
  games: number
  /** Part du genre dans le pays ÷ part du genre partout : au-dessus de 1, il est surreprésenté. */
  index: number
}

export interface StudioCountry {
  iso3: string
  name: string
  studios: number
  games: number
  favorite_genre: string | null
  favorite_index: number | null
  top_genres: StudioGenreScore[]
  top_studios: { name: string; games: number }[]
}

export interface StudioCountriesStats {
  is_sample: boolean
  countries: StudioCountry[]
}
