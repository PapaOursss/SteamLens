<template>
  <ChartFrame :option="option" :height="height" :label="label" />
  <ScaleLegend low="0" :high="formatNumber(maxVal)" no-data-label="Aucune sortie" />
</template>

<script setup lang="ts">
import { chartBase, escapeHtml } from '~/utils/chartBase'
import { formatNumber } from '~/utils/format'
import { COLORS, NO_DATA_COLOR, SEQUENTIAL_COLORS } from '~/utils/tokens'

const props = withDefaults(
  defineProps<{
    data: [string, number][]
    year: number
    height?: number
    label?: string
  }>(),
  {
    height: 240,
    label: 'Calendrier annuel des sorties de jeux (style contributions)'
  }
)

const maxVal = computed(() => Math.max(1, ...props.data.map((c) => c[1])))

function tooltipText(params: { value: [string, number] }): string {
  const [dateStr, count] = params.value
  return `<strong>${escapeHtml(dateStr)}</strong><br><strong>${formatNumber(count)} jeux sortis</strong>`
}

const option = computed(() => {
  const base = chartBase()
  return {
    ...base,
    tooltip: { ...base.tooltip, formatter: tooltipText },
    visualMap: {
      min: 0,
      max: maxVal.value,
      show: false,
      inRange: { color: [...SEQUENTIAL_COLORS] }
    },
    calendar: {
      top: 30,
      left: 40,
      right: 30,
      cellSize: ['auto', 18],
      range: props.year,
      itemStyle: {
        color: NO_DATA_COLOR,
        borderColor: COLORS.ground,
        borderWidth: 2
      },
      splitLine: {
        lineStyle: { color: COLORS.line, width: 1 }
      },
      yearLabel: { show: false },
      dayLabel: { color: COLORS.soft, firstDay: 1, nameMap: 'FR' },
      monthLabel: { color: COLORS.soft, nameMap: 'FR' }
    },
    series: [
      {
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: props.data
      }
    ]
  }
})
</script>
