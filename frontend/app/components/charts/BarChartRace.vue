<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { RaceGameEntry } from '~/composables/usePlayerRace'

const GRID = { left: 160, right: 60, top: 20, bottom: 20 }

const props = defineProps<{
  entries: RaceGameEntry[]
  currentMonth: string
  height?: number
  label: string
}>()

const sortedEntries = computed(() =>
  [...props.entries].sort((a, b) => a.players - b.players)
)

const option = computed(() => ({
  ...chartBase(),
  grid: GRID,
  xAxis: {
    type: 'value',
    ...axisStyle(),
    axisLabel: {
      color: COLORS.soft,
      formatter: (val: number) => formatCompactNumber(val)
    }
  },
  yAxis: {
    type: 'category',
    data: sortedEntries.value.map((e) => e.name),
    ...axisStyle(),
    axisLabel: {
      color: COLORS.text,
      fontSize: 12,
      width: 140,
      overflow: 'truncate'
    }
  },
  series: [
    {
      type: 'bar',
      data: sortedEntries.value.map((e) => e.players),
      label: {
        show: true,
        position: 'right',
        valueAnimation: true,
        formatter: (params: { value: number }) => formatCompactNumber(params.value),
        color: COLORS.text
      },
      itemStyle: {
        color: COLORS.hot,
        borderRadius: [0, 4, 4, 0]
      },
      animationDuration: 300,
      animationDurationUpdate: 800,
      animationEasing: 'linear',
      animationEasingUpdate: 'linear'
    }
  ],
  graphic: [
    {
      type: 'text',
      right: 80,
      bottom: 40,
      style: {
        text: props.currentMonth,
        font: 'bold 48px sans-serif',
        fill: COLORS.raised
      },
      z: 100
    }
  ]
}))
</script>
