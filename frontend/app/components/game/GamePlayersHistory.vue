<template>
  <DataBlock
    :title="title"
    :note="`Joueurs connectés, moyenne par ${ZOOMS[zoom].noun}. Steam Charts, puis relevés de SteamLens.`"
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!points.length"
    empty-message="Aucun relevé de joueurs pour ce jeu."
    :height="320"
    @retry="refresh()"
  >
    <template v-if="hasZoom" #actions>
      <SegmentedControl v-model="zoom" :options="ZOOM_OPTIONS" label="Moyenne par" />
    </template>
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
import type { ChoiceOption, PlayerCountSnapshotItem, TimePoint } from '~/types'

type Zoom = 'day' | 'month' | 'year'

const props = defineProps<{ appid: number; name: string; heading?: string; hasZoom?: boolean }>()

/** Chaque zoom garde le début de la date ISO (`2024-03-15`) et le complète en jour entier. */
const ZOOMS: Record<Zoom, { label: string; noun: string; keyLength: number; dateEnd: string }> = {
  day: { label: 'Jour', noun: 'jour', keyLength: 10, dateEnd: '' },
  month: { label: 'Mois', noun: 'mois', keyLength: 7, dateEnd: '-01' },
  year: { label: 'Année', noun: 'année', keyLength: 4, dateEnd: '-01-01' }
}
const ZOOM_OPTIONS: ChoiceOption<Zoom>[] = (Object.keys(ZOOMS) as Zoom[]).map((value) => ({
  value,
  label: ZOOMS[value].label
}))

const zoom = ref<Zoom>('month')

const { data, isLoading, hasError, refresh } = useApiResource<PlayerCountSnapshotItem[]>(
  () => `/games/${props.appid}/players/`
)

/** Relevés mensuels et relevés horaires se mêlent : une moyenne par période rend la courbe lisible. */
function periodAverages(snapshots: PlayerCountSnapshotItem[], period: Zoom): TimePoint[] {
  const { keyLength, dateEnd } = ZOOMS[period]
  const periods = new Map<string, { sum: number; count: number }>()
  for (const { taken_at: takenAt, players } of snapshots) {
    if (players <= 0) continue
    const key = takenAt.slice(0, keyLength)
    const total = periods.get(key) ?? { sum: 0, count: 0 }
    periods.set(key, { sum: total.sum + players, count: total.count + 1 })
  }
  return [...periods].map(([key, { sum, count }]) => ({
    date: `${key}${dateEnd}`,
    value: Math.round(sum / count)
  }))
}

const points = computed(() => periodAverages(data.value ?? [], zoom.value))

const title = computed(() => {
  const start = points.value[0]?.date
  const since = start ? ` depuis ${new Date(start).getFullYear()}` : ''
  return `${props.heading ?? props.name}${since}`
})
</script>
