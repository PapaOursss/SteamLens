<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { RaceGameEntry } from '~/composables/usePlayerRace'

const GRID = { left: 160, right: 60, top: 20, bottom: 20 }
const MAX_TRACKED_GAMES = 10

// Même palette catégorielle par défaut d'ECharts (utilisée par BumpChart)
const ECHARTS_PALETTE = [
  '#5070dd',
  '#b6d634',
  '#505372',
  '#ff994d',
  '#0ca8df',
  '#ffd10a',
  '#fb628b',
  '#785db0',
  '#3fbe95'
]

const props = defineProps<{
  entries: RaceGameEntry[]
  currentMonth: string
  height?: number
  label: string
  timeline?: Record<string, RaceGameEntry[]>
  months?: string[]
}>()

// Même sélection et ordre de jeux que le BumpChart pour garantir des couleurs identiques
const gameColorMap = computed(() => {
  const map = new Map<string, string>()
  if (!props.timeline || !props.months) return map

  const counts: Record<string, { appid: number; count: number }> = {}
  for (const m of props.months) {
    const list = props.timeline[m] || []
    list.slice(0, 5).forEach((item) => {
      const tracked = counts[item.name] ?? { appid: item.appid, count: 0 }
      tracked.count++
      counts[item.name] = tracked
    })
  }

  const topGames = Object.keys(counts)
    .sort((a, b) => (counts[b]?.count ?? 0) - (counts[a]?.count ?? 0))
    .slice(0, MAX_TRACKED_GAMES)

  topGames.forEach((name, index) => {
    map.set(name, ECHARTS_PALETTE[index % ECHARTS_PALETTE.length])
  })

  return map
})

const sortedEntries = computed(() =>
  [...props.entries].sort((a, b) => a.players - b.players)
)

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  xAxis: {
    type: 'value',
    ...axisStyle(),
    axisLabel: {
      color: COLORS.soft,
      formatter: (val: number) => formatCompact(val)
    }
  },
  yAxis: {
    type: 'category',
    data: sortedEntries.value.map((e) => e.name),
    ...axisStyle(),
    axisLabel: {
      color: COLORS.text,
      fontSize: 12,
      width: 140,
      overflow: 'truncate'
    }
  },
  series: [
    {
      type: 'bar',
      data: sortedEntries.value.map((e) => ({
        value: e.players,
        itemStyle: {
          color: gameColorMap.value.get(e.name) ?? COLORS.hot,
          borderRadius: [0, 4, 4, 0]
        }
      })),
      label: {
        show: true,
        position: 'right',
        valueAnimation: true,
        formatter: (params: { value: number }) => formatCompact(params.value),
        color: COLORS.text
      },
      animationDuration: 300,
      animationDurationUpdate: 800,
      animationEasing: 'linear',
      animationEasingUpdate: 'linear'
    }
  ],
  graphic: [
    {
      type: 'text',
      right: 80,
      bottom: 40,
      style: {
        text: props.currentMonth,
        font: 'bold 48px sans-serif',
        fill: COLORS.raised
      },
      z: 100
    }
  ]
}))
</script>
