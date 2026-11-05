/**
 * Seule source des couleurs du site : Tailwind (`nuxt.config.ts`) et ECharts la lisent.
 * Contrastes calculés : `text` et `soft` dépassent 6,7:1 sur les trois fonds, `hot` 9:1 sur
 * `ground` et `deep`, `line` 3:1 sur `ground`. Le focus est `hot` sur tous les fonds.
 */
export const COLORS = {
  ground: '#1B1F6B',
  deep: '#12154A',
  raised: '#2A2F8F',
  text: '#F4F3FF',
  soft: '#C5C7F2',
  hot: '#FFC53D',
  line: '#6A70D6'
} as const

/** Séries distinctes (3 au plus), validées contre `deep` pour le daltonisme. */
export const SERIES_COLORS = ['#C98500', '#2E97D4', '#E0628F'] as const

/** Grandeurs : un seul ton, de l'indigo (peu) au presque blanc (beaucoup). */
export const SEQUENTIAL_COLORS = ['#3D42A0', '#5359BE', '#9CA0EC', '#CDCFF7', '#F4F3FF'] as const

/** Territoire ou tuile sans donnée : plus sombre que la plus petite valeur. */
export const NO_DATA_COLOR = COLORS.deep

export const FONT_BODY = '"Instrument Sans", system-ui, sans-serif'
