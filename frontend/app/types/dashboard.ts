export interface DashboardOverview {
  games_count: number
  total_players: number
  top_genre: string
  average_price_eur: number
}

export interface DashboardTopGame {
  appid: number
  name: string
  header_image: string
  players: number
  sparkline: number[]
}

export interface DashboardGem {
  appid: number
  name: string
  header_image: string
  short_description: string
  price_eur: number
}

export interface DashboardData {
  overview: DashboardOverview
  top_games: DashboardTopGame[]
  featured_gem: DashboardGem | null
}
