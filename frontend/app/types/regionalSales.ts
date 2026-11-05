export type RegionKey = 'na' | 'eu' | 'jp' | 'other'

export interface RegionDetails {
  id: RegionKey
  code: string
  name: string
  color: string
  totalSales: number
  topGenre: string
  topGenreShare: string
  description: string
  maxGenreVolume: number
  topGenres: Array<{ genre: string; volume: number }>
  hits: string[]
}

export const REGIONS_LIST = [
  { id: 'na' as RegionKey, label: 'Amérique du Nord', color: '#38bdf8' },
  { id: 'eu' as RegionKey, label: 'Europe', color: '#34d399' },
  { id: 'jp' as RegionKey, label: 'Japon', color: '#f43f5e' },
  { id: 'other' as RegionKey, label: 'Reste du Monde', color: '#fbbf24' }
]

export const REGIONS_DATA: Record<RegionKey, RegionDetails> = {
  na: {
    id: 'na',
    code: 'na',
    name: 'Amérique du Nord (USA, Canada, Mexique)',
    color: '#38bdf8',
    totalSales: 4392.9,
    topGenre: 'Action',
    topGenreShare: '20.0%',
    description: 'Premier marché mondial historique. Forte appétence pour les jeux d action, les jeux de tir multijoueurs (Shooters) et les simulations sportives.',
    maxGenreVolume: 877.8,
    topGenres: [
      { genre: 'Action', volume: 877.8 },
      { genre: 'Sports', volume: 683.3 },
      { genre: 'Shooter', volume: 582.6 }
    ],
    hits: ['Call of Duty: Modern Warfare 3', 'Grand Theft Auto V', 'Super Mario Bros.']
  },
  eu: {
    id: 'eu',
    code: 'eu',
    name: 'Europe (Tous pays confondus)',
    color: '#34d399',
    totalSales: 2434.1,
    topGenre: 'Action',
    topGenreShare: '21.6%',
    description: 'Bassin hétérogène dominé par le football, l action-aventure cinématographique et les jeux de course.',
    maxGenreVolume: 525.0,
    topGenres: [
      { genre: 'Action', volume: 525.0 },
      { genre: 'Sports', volume: 376.5 },
      { genre: 'Shooter', volume: 313.2 }
    ],
    hits: ['Grand Theft Auto V', 'FIFA 15 / 16', 'Mario Kart Wii']
  },
  jp: {
    id: 'jp',
    code: 'jp',
    name: 'Japon',
    color: '#f43f5e',
    totalSales: 1284.3,
    topGenre: 'Role-Playing (J-RPG)',
    topGenreShare: '26.8%',
    description: 'Marché aux spécificités uniques au monde : les J-RPG surpassent tous les autres genres réunis. Les jeux de tir occidentaux y sont historiquement très marginaux.',
    maxGenreVolume: 344.9,
    topGenres: [
      { genre: 'Role-Playing (RPG)', volume: 344.9 },
      { genre: 'Action', volume: 159.9 },
      { genre: 'Sports', volume: 135.4 }
    ],
    hits: ['Pokémon Rouge / Bleu / Vert', 'Dragon Quest IX', 'Monster Hunter Freedom 3']
  },
  other: {
    id: 'other',
    code: 'other',
    name: 'Reste du Monde (Amérique du Sud, Asie, Océanie, Afrique)',
    color: '#fbbf24',
    totalSales: 797.7,
    topGenre: 'Action',
    topGenreShare: '23.4%',
    description: 'Zones émergentes et marchés variés combinant l Asie-Pacifique, le Brésil et le Moyen-Orient.',
    maxGenreVolume: 187.5,
    topGenres: [
      { genre: 'Action', volume: 187.5 },
      { genre: 'Sports', volume: 134.9 },
      { genre: 'Shooter', volume: 102.7 }
    ],
    hits: ['Grand Theft Auto: San Andreas', 'FIFA', 'Gran Turismo 4']
  }
}
