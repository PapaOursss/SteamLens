<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { TimePoint } from '~/types'

interface AxisTooltipParam {
  value: [string, number]
}

const AREA_OPACITY = 0.1
const LINE_WIDTH = 2
const GRID = { left: 56, right: 16, top: 16, bottom: 32 }

const props = defineProps<{
  points: TimePoint[]
  height: number
  label: string
  formatValue: (value: number) => string
  formatAxis: (value: number) => string
}>()

function tooltipText(params: AxisTooltipParam[]): string {
  const [date, value] = params[0]!.value
  return `${formatDate(date)}<br><strong>${props.formatValue(value)}</strong>`
}

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  tooltip: { ...chartBase().tooltip, trigger: 'axis', formatter: tooltipText },
  xAxis: { type: 'time', ...axisStyle(), splitLine: { show: false } },
  yAxis: {
    type: 'value',
    ...axisStyle(),
    axisLine: { show: false },
    axisLabel: { color: COLORS.soft, formatter: props.formatAxis }
  },
  series: [
    {
      type: 'line',
      data: props.points.map((point) => [point.date, point.value]),
      showSymbol: false,
      sampling: 'lttb',
      lineStyle: { color: COLORS.hot, width: LINE_WIDTH },
      itemStyle: { color: COLORS.hot },
      areaStyle: { color: COLORS.hot, opacity: AREA_OPACITY }
    }
  ]
}))
</script>
