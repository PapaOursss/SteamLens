import type { RegionalGenreSales, SalesRegionKey } from '~/types'

export interface SalesRegion {
  key: SalesRegionKey
  label: string
  area: string
  color: string
  description: string
  hits: string[]
}

/** Les quatre marchés de vgsales ; les trois premiers prennent les trois premières séries. */
export const SALES_REGIONS: SalesRegion[] = [
  {
    key: 'na',
    label: 'Amérique du Nord',
    area: 'États-Unis, Canada, Mexique',
    get color() { return seriesColor(0) },
    description: "Premier marché historique : jeux d'action, jeux de tir multijoueurs et simulations sportives.",
    hits: ['Call of Duty: Modern Warfare 3', 'Grand Theft Auto V', 'Super Mario Bros.']
  },
  {
    key: 'eu',
    label: 'Europe',
    area: 'Tous pays confondus',
    get color() { return seriesColor(1) },
    description: "Un marché varié, porté par le football, l'action-aventure et les jeux de course.",
    hits: ['Grand Theft Auto V', 'FIFA 15 / 16', 'Mario Kart Wii']
  },
  {
    key: 'jp',
    label: 'Japon',
    area: 'Un seul pays, le troisième marché',
    get color() { return seriesColor(2) },
    description: 'Le seul marché où le jeu de rôle passe devant tout le reste ; les jeux de tir y restent marginaux.',
    hits: ['Pokémon Rouge / Bleu / Vert', 'Dragon Quest IX', 'Monster Hunter Freedom 3']
  },
  {
    key: 'other',
    label: 'Reste du monde',
    area: 'Amérique du Sud, Afrique, Asie, Océanie',
    get color() { return COLORS.line },
    description: 'Les marchés émergents : Asie-Pacifique, Brésil, Moyen-Orient, où les franchises mondiales dominent.',
    hits: ['Grand Theft Auto: San Andreas', 'FIFA', 'Gran Turismo 4']
  }
]

export function regionTotal(sales: RegionalGenreSales[], key: SalesRegionKey): number {
  return sales.reduce((total, row) => total + row[key], 0)
}

export function worldTotal(row: RegionalGenreSales): number {
  return row.na + row.eu + row.jp + row.other
}
