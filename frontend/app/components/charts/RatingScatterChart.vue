<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { RatingPoint } from '~/types'

const props = withDefaults(
  defineProps<{
    points: RatingPoint[]
    height?: number
    label: string
  }>(),
  { height: 450 }
)

const AXIS_MIN = 40
const PERCENT = 100
const POINT_SIZE = 9
const POINT_OPACITY = 0.75

function tooltipText(params: { data: [number, number, RatingPoint] }): string {
  const item = params.data[2]
  const rawg = item.rawg_rating ? `<br>RAWG : <strong>${formatNumber(item.rawg_rating)}/5</strong>` : ''
  return `<strong>${escapeHtml(item.name)}</strong><br>`
    + `Metacritic : <strong>${item.press_score}/100</strong><br>`
    + `Avis Steam : <strong>${formatPercent(item.steam_score)}</strong>${rawg}`
}

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltipText },
  grid: { left: 56, right: 24, top: 24, bottom: 56 },
  xAxis: {
    type: 'value',
    name: 'Note Metacritic (presse)',
    nameLocation: 'middle',
    nameGap: 32,
    min: AXIS_MIN,
    max: PERCENT,
    ...axisStyle()
  },
  yAxis: {
    type: 'value',
    name: 'Avis positifs sur Steam',
    nameLocation: 'middle',
    nameGap: 40,
    min: AXIS_MIN,
    max: PERCENT,
    ...axisStyle(),
    axisLabel: { color: COLORS.soft, formatter: '{value} %' }
  },
  series: [
    {
      name: 'Accord parfait',
      type: 'line',
      data: [[AXIS_MIN, AXIS_MIN], [PERCENT, PERCENT]],
      lineStyle: { type: 'dashed', color: COLORS.soft, width: 1 },
      symbol: 'none',
      silent: true,
      tooltip: { show: false }
    },
    {
      name: 'Jeux',
      type: 'scatter',
      symbolSize: POINT_SIZE,
      itemStyle: { color: COLORS.hot, opacity: POINT_OPACITY, borderColor: COLORS.deep, borderWidth: 1 },
      data: props.points.map((point) => [point.press_score, point.steam_score, point])
    }
  ]
}))
</script>
