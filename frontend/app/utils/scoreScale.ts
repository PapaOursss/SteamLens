export interface ScoreLevel {
  label: string
  minimum: number
  fill: string
  ink: string
}

/** Note moyenne (0 = pas de note). Du moins bon au meilleur : plus c'est clair, mieux c'est noté. */
export const SCORE_LEVELS: ScoreLevel[] = [
  { label: 'Moins de 60', minimum: 1, fill: SEQUENTIAL_COLORS[0], ink: COLORS.text },
  { label: '60 à 69', minimum: 60, fill: SEQUENTIAL_COLORS[1], ink: COLORS.text },
  { label: '70 à 79', minimum: 70, fill: SEQUENTIAL_COLORS[2], ink: COLORS.deep },
  { label: '80 à 89', minimum: 80, fill: SEQUENTIAL_COLORS[3], ink: COLORS.deep },
  { label: '90 et plus', minimum: 90, fill: SEQUENTIAL_COLORS[4], ink: COLORS.deep }
]

export const NO_SCORE_LEVEL: ScoreLevel = {
  label: 'Pas de note',
  minimum: 0,
  fill: NO_DATA_COLOR,
  ink: COLORS.text
}

export function scoreLevel(score: number): ScoreLevel {
  return [...SCORE_LEVELS].reverse().find((level) => score >= level.minimum) ?? NO_SCORE_LEVEL
}
