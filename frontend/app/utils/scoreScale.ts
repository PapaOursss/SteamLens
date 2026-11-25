export interface ScoreLevel {
  label: string
  minimum: number
  fill: string
  ink: string
}

/** Note moyenne (0 = pas de note). Du moins bon au meilleur : plus c'est clair, mieux c'est noté. */
export const SCORE_LEVELS: ScoreLevel[] = [
  { label: 'Moins de 60', minimum: 1, get fill() { return SEQUENTIAL_COLORS[0] }, get ink() { return COLORS.text } },
  { label: '60 à 69', minimum: 60, get fill() { return SEQUENTIAL_COLORS[1] }, get ink() { return COLORS.text } },
  { label: '70 à 79', minimum: 70, get fill() { return SEQUENTIAL_COLORS[2] }, get ink() { return COLORS.deep } },
  { label: '80 à 89', minimum: 80, get fill() { return SEQUENTIAL_COLORS[3] }, get ink() { return COLORS.deep } },
  { label: '90 et plus', minimum: 90, get fill() { return SEQUENTIAL_COLORS[4] }, get ink() { return COLORS.deep } }
]

export const NO_SCORE_LEVEL: ScoreLevel = {
  label: 'Pas de note',
  minimum: 0,
  get fill() { return COLORS.deep },
  get ink() { return COLORS.text }
}

export function scoreLevel(score: number): ScoreLevel {
  return [...SCORE_LEVELS].reverse().find((level) => score >= level.minimum) ?? NO_SCORE_LEVEL
}
