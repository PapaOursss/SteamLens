export interface ScoreLevel {
  label: string
  minimum: number
  fill: string
  ink: string
}

/**
 * Note Metacritic moyenne d'un tag (0 = pas de note). Les moyennes se tassent entre 70 et 78 :
 * des tranches de dix points les mettaient presque toutes dans la même couleur. Ces bornes
 * suivent leur répartition (environ un cinquième des tags par tranche). Plus clair, mieux noté.
 */
export const SCORE_LEVELS: ScoreLevel[] = [
  { label: 'Moins de 70', minimum: 1, get fill() { return SEQUENTIAL_COLORS[0] }, get ink() { return COLORS.text } },
  { label: '70 à 72', minimum: 70, get fill() { return SEQUENTIAL_COLORS[1] }, get ink() { return COLORS.text } },
  { label: '73 à 74', minimum: 73, get fill() { return SEQUENTIAL_COLORS[2] }, get ink() { return COLORS.deep } },
  { label: '75 à 76', minimum: 75, get fill() { return SEQUENTIAL_COLORS[3] }, get ink() { return COLORS.deep } },
  { label: '77 et plus', minimum: 77, get fill() { return SEQUENTIAL_COLORS[4] }, get ink() { return COLORS.deep } }
]

export const NO_SCORE_LEVEL: ScoreLevel = {
  label: 'Pas de note',
  minimum: 0,
  get fill() { return COLORS.deep },
  get ink() { return COLORS.soft }
}

export function scoreLevel(score: number): ScoreLevel {
  return [...SCORE_LEVELS].reverse().find((level) => score >= level.minimum) ?? NO_SCORE_LEVEL
}
