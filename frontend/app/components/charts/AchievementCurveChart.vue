<template>
  <ChartFrame :option="option" :height="HEIGHT" :label="label" />
</template>

<script setup lang="ts">
import type { AchievementStep } from '~/types'

interface AxisTooltipParam {
  dataIndex: number
}

const HEIGHT = 320
const PERCENT = 100
const LINE_WIDTH = 2
const AREA_OPACITY = 0.1
const STEP_SIZE = 4
const ENDING_SIZE = 12
const GRID = { left: 56, right: 16, top: 16, bottom: 32 }

const props = defineProps<{ curve: AchievementStep[]; label: string }>()

function tooltipText(params: AxisTooltipParam[]): string {
  const step = props.curve[params[0]!.dataIndex]!
  return `${escapeHtml(step.name)}<br><strong>${formatPercent(step.percent)} des joueurs</strong>`
}

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  tooltip: { ...chartBase().tooltip, trigger: 'axis', formatter: tooltipText },
  xAxis: { type: 'category', data: props.curve.map((step) => step.rank), ...axisStyle(), splitLine: { show: false } },
  yAxis: { type: 'value', min: 0, max: PERCENT, ...axisStyle(), axisLine: { show: false }, axisLabel: { color: COLORS.soft, formatter: '{value} %' } },
  series: [
    {
      type: 'line',
      symbol: 'circle',
      lineStyle: { color: COLORS.soft, width: LINE_WIDTH },
      areaStyle: { color: COLORS.soft, opacity: AREA_OPACITY },
      data: props.curve.map((step) => ({
        value: step.percent,
        symbolSize: step.is_ending ? ENDING_SIZE : STEP_SIZE,
        itemStyle: { color: step.is_ending ? COLORS.hot : COLORS.soft }
      }))
    }
  ]
}))
</script>
