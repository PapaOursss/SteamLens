import { reactive } from 'vue'
import {
  CATEGORICAL_PALETTES,
  DEFAULT_THEME,
  PALETTES,
  SEQUENTIAL_PALETTES,
  STATUS_PALETTES,
  type Categorical,
  type Palette,
  type Scale,
  type StatusColors,
  type ThemeName
} from './palettes'

/** Couleurs du thème actif, réactives : un graphique calculé avec elles suit le thème. */
export const COLORS = reactive<Palette>({ ...PALETTES[DEFAULT_THEME] })

export const SEQUENTIAL_COLORS = reactive<Scale>([...SEQUENTIAL_PALETTES[DEFAULT_THEME]])

/** Séries distinctes, dans l'ordre : `SERIES_COLORS[0]` pour la première, et ainsi de suite. */
export const SERIES_COLORS = reactive<Categorical>([...CATEGORICAL_PALETTES[DEFAULT_THEME]])

export const STATUS_COLORS = reactive<StatusColors>({ ...STATUS_PALETTES[DEFAULT_THEME] })

/** Couleur de la n-ième série ; au-delà de huit, la teinte neutre des « Autres ». */
export function seriesColor(index: number): string {
  return SERIES_COLORS[index] ?? COLORS.line
}

export const FONT_BODY = '"Instrument Sans", system-ui, sans-serif'
export const FONT_DISPLAY = '"Bricolage Grotesque", system-ui, sans-serif'

export function applyPalette(theme: ThemeName) {
  Object.assign(COLORS, PALETTES[theme])
  SEQUENTIAL_COLORS.splice(0, SEQUENTIAL_COLORS.length, ...SEQUENTIAL_PALETTES[theme])
  SERIES_COLORS.splice(0, SERIES_COLORS.length, ...CATEGORICAL_PALETTES[theme])
  Object.assign(STATUS_COLORS, STATUS_PALETTES[theme])
}
