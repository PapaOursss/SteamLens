/**
 * Seule source des couleurs du site : Tailwind (`nuxt.config.ts`) et ECharts la lisent.
 * Sombre : `text` et `soft` dépassent 6,7:1 sur les trois fonds, `hot` 9:1 sur `ground` et `deep`.
 * Clair : les mêmes rôles, clair et foncé échangés ; `hot` reste lisible en texte.
 */
export type ThemeName = 'dark' | 'light'

export const DEFAULT_THEME: ThemeName = 'dark'
export const THEME_STORAGE_KEY = 'steamlens-theme'

export interface Palette {
  ground: string
  deep: string
  raised: string
  text: string
  soft: string
  hot: string
  line: string
}

export const PALETTES: Record<ThemeName, Palette> = {
  dark: {
    ground: '#1B1F6B',
    deep: '#12154A',
    raised: '#2A2F8F',
    text: '#F4F3FF',
    soft: '#C5C7F2',
    hot: '#FFC53D',
    line: '#6A70D6'
  },
  light: {
    ground: '#F7F7FF',
    deep: '#E6E7FB',
    raised: '#D3D6F6',
    text: '#12154A',
    soft: '#3A3F8A',
    hot: '#7A4B00',
    line: '#6A70D6'
  }
}

export type Scale = [string, string, string, string, string]

/** Grandeurs : un seul ton, du plus proche du fond (peu) au plus contrasté (beaucoup). */
export const SEQUENTIAL_PALETTES: Record<ThemeName, Scale> = {
  dark: ['#3D42A0', '#5359BE', '#9CA0EC', '#CDCFF7', '#F4F3FF'],
  light: ['#CDCFF7', '#9CA0EC', '#5359BE', '#3D42A0', '#1B1F6B']
}

function rgbChannels(hex: string): string {
  return [1, 3, 5].map((start) => Number.parseInt(hex.slice(start, start + 2), 16)).join(' ')
}

function cssVariables(palette: Palette): string {
  return Object.entries(palette).map(([name, hex]) => `--${name}:${rgbChannels(hex)}`).join(';')
}

/** Feuille posée dans le `<head>` : le mode clair ne change que des variables. */
export const THEME_STYLESHEET = [
  `:root{color-scheme:dark;${cssVariables(PALETTES.dark)}}`,
  `:root[data-theme=light]{color-scheme:light;${cssVariables(PALETTES.light)}}`
].join('')

/** Appliqué avant le premier affichage, pour ne pas montrer le mauvais thème un instant. */
export const THEME_BOOT_SCRIPT = `try{if(localStorage.getItem('${THEME_STORAGE_KEY}')==='light')document.documentElement.dataset.theme='light'}catch{}`
