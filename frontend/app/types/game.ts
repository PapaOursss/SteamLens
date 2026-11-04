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
  genres: string[]
  tags: GameTag[]
  themes: string[]
  game_modes: string[]
  platforms: string[]
  developers: string[]
  publishers: string[]
}
