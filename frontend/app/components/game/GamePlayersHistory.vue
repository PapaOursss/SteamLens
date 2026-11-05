<template>
  <DataBlock
    :title="title"
    note="Joueurs connectés, moyenne par mois. Steam Charts, puis relevés de SteamLens."
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!points.length"
    empty-message="Aucun relevé de joueurs pour ce jeu."
    :height="320"
    @retry="refresh()"
  >
    <TimeLineChart
      :points="points"
      :height="320"
      :label="`Nombre de joueurs de ${name} au fil du temps`"
      :format-value="formatNumber"
      :format-axis="formatCompact"
    />
  </DataBlock>
</template>

<script setup lang="ts">
import type { PlayerCountSnapshotItem, TimePoint } from '~/types'

const props = defineProps<{ appid: number; name: string }>()

const { data, isLoading, hasError, refresh } = useApiResource<PlayerCountSnapshotItem[]>(
  () => `/games/${props.appid}/players/`
)

const MONTH_LENGTH = 7

/** Relevés mensuels et relevés horaires se mêlent : une moyenne par mois rend la courbe lisible. */
function monthlyAverages(snapshots: PlayerCountSnapshotItem[]): TimePoint[] {
  const months = new Map<string, { sum: number; count: number }>()
  for (const { taken_at: takenAt, players } of snapshots) {
    if (players <= 0) continue
    const month = takenAt.slice(0, MONTH_LENGTH)
    const total = months.get(month) ?? { sum: 0, count: 0 }
    months.set(month, { sum: total.sum + players, count: total.count + 1 })
  }
  return [...months].map(([month, { sum, count }]) => ({
    date: `${month}-01`,
    value: Math.round(sum / count)
  }))
}

const points = computed(() => monthlyAverages(data.value ?? []))

const title = computed(() => {
  const start = points.value[0]?.date
  const since = start ? ` depuis ${new Date(start).getFullYear()}` : ''
  return `${props.name}${since}`
})
</script>
