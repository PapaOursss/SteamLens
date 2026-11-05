<template>
  <ChartFrame :option="option" :height="HEIGHT" :label="label" />
</template>

<script setup lang="ts">
import type { PriceChangeRow } from '~/types'

const HEIGHT = 320
const LINE_WIDTH = 2
const GRID = { left: 64, right: 16, top: 40, bottom: 32 }
const PAID = 'Prix payé'
const REGULAR = 'Prix hors promo'

const props = defineProps<{ changes: PriceChangeRow[]; currency: string | null; label: string }>()

function formatValue(value: number): string {
  return formatAmount(value, props.currency)
}

function stepLine(name: string, color: string, type: string, pick: (change: PriceChangeRow) => number) {
  return {
    name,
    type: 'line',
    step: 'end',
    showSymbol: false,
    lineStyle: { color, type, width: LINE_WIDTH },
    itemStyle: { color },
    data: props.changes.map((change) => [change.changed_at, pick(change)])
  }
}

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  legend: { data: [PAID, REGULAR], textStyle: { color: COLORS.text } },
  tooltip: {
    ...chartBase().tooltip,
    trigger: 'axis',
    valueFormatter: formatValue
  },
  xAxis: { type: 'time', ...axisStyle(), splitLine: { show: false } },
  yAxis: { type: 'value', ...axisStyle(), axisLine: { show: false }, axisLabel: { color: COLORS.soft, formatter: formatValue } },
  series: [
    stepLine(REGULAR, COLORS.soft, 'dashed', (change) => change.regular),
    stepLine(PAID, COLORS.hot, 'solid', (change) => change.price)
  ]
}))
</script>
