<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import { trackedRaceGames, type RaceGameEntry } from '~/composables/usePlayerRace'

const GRID = { left: 160, right: 60, top: 20, bottom: 20 }

const props = defineProps<{
  entries: RaceGameEntry[]
  currentMonth: string
  height?: number
  label: string
  timeline?: Record<string, RaceGameEntry[]>
  months?: string[]
}>()

/** Les jeux suivis gardent leur couleur de série (comme dans BumpChart), les autres restent neutres. */
const gameColors = computed(() => {
  if (!props.timeline || !props.months) return new Map<string, string>()
  const tracked = trackedRaceGames(props.months, props.timeline)
  return new Map(tracked.map((name, index) => [name, seriesColor(index)]))
})

function barColor(name: string): string {
  return gameColors.value.get(name) ?? (props.timeline ? COLORS.line : COLORS.hot)
}

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
          color: barColor(e.name),
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
        text: formatMonth(props.currentMonth),
        font: `800 48px ${FONT_DISPLAY}`,
        fill: COLORS.raised
      },
      z: 100
    }
  ]
}))
</script>
