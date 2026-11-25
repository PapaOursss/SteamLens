<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { TimePoint } from '~/types'

const props = defineProps<{
  series: { name: string; points: TimePoint[] }[]
  height: number
  label: string
  isStep?: boolean
  formatValue: (value: number) => string
}>()

const option = computed(() => ({
  ...chartBase(),
  grid: { left: 64, right: 16, top: 16, bottom: 64 },
  legend: { bottom: 0, textStyle: { color: COLORS.text } },
  tooltip: { ...chartBase().tooltip, trigger: 'axis', valueFormatter: props.formatValue },
  xAxis: { type: 'time', ...axisStyle(), splitLine: { show: false } },
  yAxis: { type: 'value', ...axisStyle(), axisLabel: { color: COLORS.soft, formatter: props.formatValue } },
  series: props.series.map((entry, index) => {
    const style = COMPARED_STYLES[index]!
    return {
      type: 'line',
      name: entry.name,
      data: entry.points.map((point) => [point.date, point.value]),
      step: props.isStep ? 'end' : false,
      showSymbol: entry.points.length === 1,
      lineStyle: { color: style.color, type: style.line, width: 2 },
      itemStyle: { color: style.color }
    }
  })
}))
</script>
