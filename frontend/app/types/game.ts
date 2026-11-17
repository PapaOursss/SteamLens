export interface GameTag {
  name: string
  votes: number
}

export interface GameListItem {
  appid: number
  name: string
  release_date: string | null
  is_free: boolean
  header_image: string
  genres: string[]
}

export interface GameDetail {
  appid: number
  name: string
  release_date: string | null
  is_free: boolean
  header_image: string
  short_description: string
  metacritic_score: number | null
  positive_share: number | null
  genres: string[]
  tags: GameTag[]
  themes: string[]
  game_modes: string[]
  platforms: string[]
  developers: string[]
  publishers: string[]
}

export type GameDnaKey = 'rating' | 'popularity' | 'price' | 'lifespan' | 'twitch' | 'achievement_rarity'

/** Un axe de l'« ADN du jeu » : rang de 0 à 100 parmi les jeux mesurés, null sans donnée. */
export interface GameDnaAxis {
  key: GameDnaKey
  score: number | null
  raw: number | null
}
