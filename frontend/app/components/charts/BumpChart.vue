<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import { trackedRaceGames, type RaceGameEntry } from '~/composables/usePlayerRace'

const GRID = { left: 40, right: 120, top: 30, bottom: 40 }
const LAST_RANK = 10

const props = defineProps<{
  months: string[]
  timeline: Record<string, RaceGameEntry[]>
  height?: number
  label: string
}>()

const trackedGames = computed(() => trackedRaceGames(props.months, props.timeline))

const series = computed(() => {
  return trackedGames.value.map((gameName, index) => {
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
      itemStyle: { color: seriesColor(index) },
      lineStyle: { width: 3, color: seriesColor(index) }
    }
  })
})

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  tooltip: {
    ...chartBase().tooltip,
    trigger: 'item',
    formatter: (params: { seriesName: string; value: number; name: string }) =>
      `${formatMonth(params.name)} : <strong>${escapeHtml(params.seriesName)}</strong>, ${params.value}<sup>e</sup>`
  },
  xAxis: {
    type: 'category',
    data: props.months,
    ...axisStyle(),
    axisLabel: {
      color: COLORS.soft,
      interval: props.months.length > 8 ? Math.floor(props.months.length / 8) : 'auto'
    }
  },
  yAxis: {
    type: 'value',
    inverse: true,
    min: 1,
    max: LAST_RANK,
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
