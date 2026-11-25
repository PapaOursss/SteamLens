import type { PlayerCountSnapshotItem, TimePoint } from '~/types'

/** Un jeu garde sa couleur et son trait d'un graphique à l'autre : la couleur n'est pas seule. */
export const COMPARED_STYLES = [
  { get color() { return seriesColor(0) }, line: 'solid' },
  { get color() { return seriesColor(1) }, line: 'dashed' },
  { get color() { return seriesColor(2) }, line: 'dotted' },
  { get color() { return seriesColor(3) }, line: [10, 4, 2, 4] }
] as const

const MONTH_LENGTH = 7

/** Moyenne par mois : relevés mensuels et horaires se mêlent dans l'historique. */
export function monthlyPlayers(snapshots: PlayerCountSnapshotItem[]): TimePoint[] {
  const months = new Map<string, { sum: number; count: number }>()
  for (const { taken_at: takenAt, players } of snapshots) {
    if (players <= 0) continue
    const month = takenAt.slice(0, MONTH_LENGTH)
    const total = months.get(month) ?? { sum: 0, count: 0 }
    months.set(month, { sum: total.sum + players, count: total.count + 1 })
  }
  return [...months].map(([month, { sum, count }]) => ({ date: `${month}-01`, value: Math.round(sum / count) }))
}
