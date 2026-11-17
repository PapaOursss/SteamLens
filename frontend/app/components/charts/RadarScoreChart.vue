<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { RadarAxis } from '~/types'

const MAX_SCORE = 100
const AREA_OPACITY = 0.25
const LINE_WIDTH = 2
const SYMBOL_SIZE = 8
const SPLIT_COUNT = 4
const RADIUS = '65%'

const props = defineProps<{ axes: RadarAxis[]; height: number; label: string }>()

function tooltipText(): string {
  return props.axes
    .map((axis) => `${escapeHtml(axis.label)} : <strong>${axis.score ?? '—'}</strong> · ${escapeHtml(axis.detail)}`)
    .join('<br>')
}

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltipText },
  radar: {
    radius: RADIUS,
    splitNumber: SPLIT_COUNT,
    indicator: props.axes.map((axis) => ({ name: axis.label, max: MAX_SCORE })),
    axisName: { color: COLORS.text },
    axisLine: { lineStyle: { color: COLORS.line } },
    splitLine: { lineStyle: { color: COLORS.raised } },
    splitArea: { show: false }
  },
  series: [
    {
      type: 'radar',
      data: [{ value: props.axes.map((axis) => axis.score ?? 0), name: props.label }],
      symbolSize: SYMBOL_SIZE,
      lineStyle: { color: COLORS.hot, width: LINE_WIDTH },
      itemStyle: { color: COLORS.hot },
      areaStyle: { color: COLORS.hot, opacity: AREA_OPACITY }
    }
  ]
}))
</script>
