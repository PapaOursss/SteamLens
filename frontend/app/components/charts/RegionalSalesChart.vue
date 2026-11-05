<template>
  <ChartFrame :option="option" :height="height" label="Ventes par genre en Amérique du Nord, en Europe et au Japon" />
</template>

<script setup lang="ts">
import type { RegionalGenreSales } from '~/types'

const ROW_HEIGHT = 72
const CHROME_HEIGHT = 72
const BAR_WIDTH = 14
const BAR_RADIUS = [0, 4, 4, 0]
const SERIES = [
  { key: 'na', name: 'Amérique du Nord' },
  { key: 'eu', name: 'Europe' },
  { key: 'jp', name: 'Japon' }
] as const

const props = defineProps<{ sales: RegionalGenreSales[] }>()

const height = computed(() => props.sales.length * ROW_HEIGHT + CHROME_HEIGHT)

const option = computed(() => ({
  ...chartBase(),
  grid: { left: 8, right: 16, top: 40, bottom: 28, containLabel: true },
  legend: { top: 0, left: 0, textStyle: { color: COLORS.text, fontFamily: FONT_BODY, fontSize: 14 } },
  tooltip: {
    ...chartBase().tooltip,
    trigger: 'axis',
    axisPointer: { type: 'shadow', shadowStyle: { color: COLORS.raised, opacity: 0.4 } },
    valueFormatter: (value: number) => `${formatNumber(value)} M`
  },
  xAxis: {
    type: 'value',
    ...axisStyle(),
    axisLine: { show: false },
    axisLabel: { color: COLORS.soft, formatter: formatNumber }
  },
  yAxis: {
    type: 'category',
    inverse: true,
    data: props.sales.map((row) => row.genre),
    ...axisStyle(),
    axisLabel: { color: COLORS.text }
  },
  series: SERIES.map((serie, index) => ({
    type: 'bar',
    name: serie.name,
    data: props.sales.map((row) => row[serie.key]),
    barWidth: BAR_WIDTH,
    barGap: '15%',
    itemStyle: { color: SERIES_COLORS[index], borderRadius: BAR_RADIUS }
  }))
}))
</script>
