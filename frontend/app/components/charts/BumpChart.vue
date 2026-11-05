<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { RaceGameEntry } from '~/composables/usePlayerRace'

const GRID = { left: 40, right: 120, top: 30, bottom: 40 }
const MAX_GAMES = 10

const props = defineProps<{
  months: string[]
  timeline: Record<string, RaceGameEntry[]>
  height?: number
  label: string
}>()

// Sélectionner les jeux qui sont apparus le plus souvent dans le top
const trackedGames = computed(() => {
  const counts: Record<string, { appid: number; count: number }> = {}
  for (const m of props.months) {
    const list = props.timeline[m] || []
    list.slice(0, 5).forEach((item) => {
      if (!counts[item.name]) counts[item.name] = { appid: item.appid, count: 0 }
      counts[item.name].count++
    })
  }
  return Object.keys(counts)
    .sort((a, b) => counts[b].count - counts[a].count)
    .slice(0, MAX_GAMES)
})

const series = computed(() => {
  return trackedGames.value.map((gameName) => {
    const data = props.months.map((m) => {
      const list = props.timeline[m] || []
      const rankIdx = list.findIndex((x) => x.name === gameName)
      return rankIdx !== -1 ? rankIdx + 1 : null
    })
    return {
      name: gameName,
      type: 'line',
      data,
      smooth: true,
      endLabel: {
        show: true,
        formatter: '{a}',
        color: COLORS.soft,
        distance: 10
      },
      lineStyle: { width: 3 }
    }
  })
})

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  tooltip: {
    trigger: 'item',
    formatter: (params: { seriesName: string; value: number; name: string }) =>
      `${params.name} : ${params.seriesName} (Rang #${params.value})`
  },
  xAxis: {
    type: 'category',
    data: props.months,
    ...axisStyle(),
    axisLabel: { color: COLORS.soft, interval: Math.floor(props.months.length / 8) }
  },
  yAxis: {
    type: 'value',
    inverse: true,
    min: 1,
    max: 10,
    ...axisStyle(),
    splitLine: { show: true, lineStyle: { color: COLORS.raised } },
    axisLabel: {
      formatter: '#{value}',
      color: COLORS.soft
    }
  },
  series: series.value
}))
</script>
