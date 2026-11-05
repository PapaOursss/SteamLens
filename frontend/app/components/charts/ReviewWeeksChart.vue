<template>
  <ChartFrame :option="option" :height="HEIGHT" :label="label" />
</template>

<script setup lang="ts">
import type { ReviewBombing, ReviewWeekRow } from '~/types'

interface AxisTooltipParam {
  value: [string, number]
}

const HEIGHT = 300
const PERCENT = 100
const LINE_WIDTH = 2
const POINT_SIZE = 12
const GRID = { left: 56, right: 16, top: 16, bottom: 32 }

const props = defineProps<{ weeks: ReviewWeekRow[]; bombings: ReviewBombing[]; label: string }>()

function tooltipText(params: AxisTooltipParam[]): string {
  const [week, share] = params[0]!.value
  return `Semaine du ${formatDate(week)}<br><strong>${formatPercent(share)} d'avis positifs</strong>`
}

const option = computed(() => {
  const bombed = new Set(props.bombings.map((row) => row.week_start))
  return {
    ...chartBase(),
    grid: GRID,
    tooltip: { ...chartBase().tooltip, trigger: 'axis', formatter: tooltipText },
    xAxis: { type: 'time', ...axisStyle(), splitLine: { show: false } },
    yAxis: { type: 'value', min: 0, max: PERCENT, ...axisStyle(), axisLine: { show: false }, axisLabel: { color: COLORS.soft, formatter: '{value} %' } },
    series: [
      {
        type: 'line',
        lineStyle: { color: COLORS.soft, width: LINE_WIDTH },
        itemStyle: { color: COLORS.soft },
        showSymbol: false,
        data: props.weeks.map((week) => {
          const isBombed = bombed.has(week.week_start)
          return {
            value: [week.week_start, Math.round(week.positive_share * PERCENT)],
            symbol: 'circle',
            symbolSize: POINT_SIZE,
            showSymbol: isBombed,
            itemStyle: { color: isBombed ? COLORS.hot : COLORS.soft }
          }
        })
      }
    ]
  }
})
</script>
