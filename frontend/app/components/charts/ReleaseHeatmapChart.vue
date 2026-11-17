<template>
  <ChartFrame :option="option" :height="height" :label="label" />
  <ScaleLegend low="0" :high="formatNumber(maxVal)" no-data-label="Aucune sortie" />
</template>

<script setup lang="ts">
import { axisStyle, chartBase } from '~/utils/chartBase'
import { formatNumber } from '~/utils/format'
import { COLORS, NO_DATA_COLOR, SEQUENTIAL_COLORS } from '~/utils/tokens'

const props = withDefaults(
  defineProps<{
    data: [number, number, number][]
    days: string[]
    months: string[]
    height?: number
    label?: string
  }>(),
  {
    height: 380,
    label: 'Répartition des sorties par jour de la semaine et par mois'
  }
)

const maxVal = computed(() => Math.max(1, ...props.data.map((c) => c[2])))

function tooltipText(params: { value: [number, number, number] }): string {
  const [dayIdx, monthIdx, count] = params.value
  const dayName = props.days[dayIdx] ?? ''
  const monthName = props.months[monthIdx] ?? ''
  return `<strong>${dayName}</strong> en <strong>${monthName}</strong><br><strong>${formatNumber(count)} sorties</strong>`
}

const option = computed(() => {
  const base = chartBase()
  return {
    ...base,
    tooltip: { ...base.tooltip, formatter: tooltipText },
    grid: { left: 80, right: 24, top: 20, bottom: 40, show: true, backgroundColor: NO_DATA_COLOR, borderWidth: 0 },
    xAxis: {
      type: 'category',
      data: props.months,
      ...axisStyle(),
      splitLine: { show: false }
    },
    yAxis: {
      type: 'category',
      data: props.days,
      ...axisStyle(),
      splitLine: { show: false }
    },
    visualMap: {
      min: 0,
      max: maxVal.value,
      show: false,
      inRange: { color: [...SEQUENTIAL_COLORS] }
    },
    series: [
      {
        type: 'heatmap',
        data: props.data.map(([d, m, val]) => [m, d, val]),
        itemStyle: { borderColor: COLORS.ground, borderWidth: 2 }
      }
    ]
  }
})
</script>
