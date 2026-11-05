<template>
  <ChartFrame :option="option" :height="height" label="Calendrier des jeux en promotion, par année et semaine" />
  <ScaleLegend low="0" :high="formatNumber(largest)" no-data-label="Aucune promo" />
</template>

<script setup lang="ts">
import type { SalesCalendar } from '~/types'

interface CellTooltipParam {
  value: [number, number, number]
}

const WEEKS_IN_YEAR = 53
const WEEK_LABEL_STEP = 4
const ROW_HEIGHT = 32
const GRID = { left: 48, right: 8, top: 8, bottom: 28 }

const props = defineProps<{ calendar: SalesCalendar }>()

const height = computed(() => props.calendar.years.length * ROW_HEIGHT + GRID.top + GRID.bottom)
const largest = computed(() => Math.max(1, ...props.calendar.cells.map((cell) => cell[2])))

function tooltipText({ value: [week, yearIndex, count] }: CellTooltipParam): string {
  return `Semaine ${week + 1} de ${props.calendar.years[yearIndex]}<br><strong>${formatNumber(count)} jeux en promo</strong>`
}

const option = computed(() => ({
  ...chartBase(),
  grid: { ...GRID, show: true, backgroundColor: NO_DATA_COLOR, borderWidth: 0 },
  tooltip: { ...chartBase().tooltip, formatter: tooltipText },
  xAxis: {
    type: 'category',
    data: Array.from({ length: WEEKS_IN_YEAR }, (_, index) => index + 1),
    ...axisStyle(),
    axisLabel: { color: COLORS.soft, interval: WEEK_LABEL_STEP - 1 },
    splitLine: { show: false }
  },
  yAxis: { type: 'category', data: props.calendar.years, ...axisStyle(), splitLine: { show: false } },
  visualMap: { min: 0, max: largest.value, show: false, inRange: { color: [...SEQUENTIAL_COLORS] } },
  series: [
    {
      type: 'heatmap',
      data: props.calendar.cells.map(([year, week, count]) => [week - 1, props.calendar.years.indexOf(year), count]),
      itemStyle: { borderColor: COLORS.ground, borderWidth: 1 }
    }
  ]
}))
</script>
