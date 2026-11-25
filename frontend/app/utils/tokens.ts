import { reactive } from 'vue'
import { DEFAULT_THEME, PALETTES, SEQUENTIAL_PALETTES, type Palette, type Scale, type ThemeName } from './palettes'

/** Couleurs du thème actif, réactives : un graphique calculé avec elles suit le thème. */
export const COLORS = reactive<Palette>({ ...PALETTES[DEFAULT_THEME] })

export const SEQUENTIAL_COLORS = reactive<Scale>([...SEQUENTIAL_PALETTES[DEFAULT_THEME]])

/** Séries distinctes (3 au plus), validées contre `deep` pour le daltonisme. */
export const SERIES_COLORS = ['#C98500', '#2E97D4', '#E0628F'] as const

export const FONT_BODY = '"Instrument Sans", system-ui, sans-serif'

export function applyPalette(theme: ThemeName) {
  Object.assign(COLORS, PALETTES[theme])
  SEQUENTIAL_COLORS.splice(0, SEQUENTIAL_COLORS.length, ...SEQUENTIAL_PALETTES[theme])
}
