<template>
  <ChartFrame :option="option" :height="height" :label="label" @click="handleClick" />
</template>

<script setup lang="ts">
import type { GameMapPoint } from '~/types'

const OTHER_FAMILY = 'Autres'
const MIN_SYMBOL_SIZE = 6
const MAX_SYMBOL_SIZE = 16
const SELECTED_SYMBOL_SIZE = 20
const MIN_LOG_OWNERS = 3
const LOG_OWNERS_RANGE = 5
const POINT_OPACITY = 0.75

const props = withDefaults(
  defineProps<{ points: GameMapPoint[]; families: string[]; selectedAppid?: number; height?: number; label: string }>(),
  { selectedAppid: undefined, height: 620 }
)

const emit = defineEmits<{ select: [point: GameMapPoint] }>()

/** Aire du point selon les propriétaires, en échelle log (de mille à cent millions). */
function symbolSize(owners: number | null): number {
  const position = (Math.log10(Math.max(owners ?? 0, 1)) - MIN_LOG_OWNERS) / LOG_OWNERS_RANGE
  const clamped = Math.min(1, Math.max(0, position))
  return Math.round(MIN_SYMBOL_SIZE + clamped * (MAX_SYMBOL_SIZE - MIN_SYMBOL_SIZE))
}

function familyColor(family: string, index: number): string {
  return family === OTHER_FAMILY ? COLORS.line : seriesColor(index)
}

function handleClick(params: { data?: { point?: GameMapPoint } }) {
  if (params.data?.point) emit('select', params.data.point)
}

function tooltip(param: { data: { point: GameMapPoint } }): string {
  const point = param.data.point
  const owners = point.owners ? `<br>~${formatCompact(point.owners)} propriétaires` : ''
  return `<strong>${escapeHtml(point.name)}</strong><br>Tag principal : ${escapeHtml(point.family)}${owners}`
}

const selectedPoint = computed(() => props.points.find((point) => point.appid === props.selectedAppid))

const option = computed(() => ({
  ...chartBase(),
  legend: { type: 'scroll', top: 0, textStyle: { color: COLORS.soft, fontFamily: FONT_BODY }, pageTextStyle: { color: COLORS.soft }, pageIconColor: COLORS.soft },
  grid: { left: 8, right: 8, top: 40, bottom: 8 },
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltip },
  xAxis: { type: 'value', show: false, scale: true },
  yAxis: { type: 'value', show: false, scale: true },
  series: [
    ...props.families.map((family, index) => ({
      name: family,
      type: 'scatter',
      itemStyle: { color: familyColor(family, index), opacity: POINT_OPACITY, borderColor: COLORS.deep, borderWidth: 1 },
      emphasis: { focus: 'series' },
      data: props.points
        .filter((point) => point.family === family)
        .map((point) => ({ value: [point.x, point.y], symbolSize: symbolSize(point.owners), point }))
    })),
    {
      name: 'Ce jeu',
      type: 'scatter',
      z: 10,
      itemStyle: { color: COLORS.text, borderColor: COLORS.deep, borderWidth: 2 },
      label: { show: true, position: 'top', formatter: '{b}', color: COLORS.text, fontWeight: 'bold' },
      data: selectedPoint.value
        ? [{ name: selectedPoint.value.name, value: [selectedPoint.value.x, selectedPoint.value.y], symbolSize: SELECTED_SYMBOL_SIZE, point: selectedPoint.value }]
        : []
    }
  ]
}))
</script>
