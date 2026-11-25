<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
const MAX_SCORE = 100

const props = defineProps<{
  axes: string[]
  series: { name: string; scores: (number | null)[] }[]
  height: number
  label: string
}>()

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, trigger: 'item' },
  legend: { bottom: 0, textStyle: { color: COLORS.text } },
  radar: {
    radius: '60%',
    indicator: props.axes.map((name) => ({ name, max: MAX_SCORE })),
    axisName: { color: COLORS.text },
    axisLine: { lineStyle: { color: COLORS.line } },
    splitLine: { lineStyle: { color: COLORS.raised } },
    splitArea: { show: false }
  },
  series: [
    {
      type: 'radar',
      data: props.series.map((entry, index) => {
        const style = COMPARED_STYLES[index]!
        return {
          name: entry.name,
          value: entry.scores.map((score) => score ?? 0),
          lineStyle: { color: style.color, type: style.line, width: 2 },
          itemStyle: { color: style.color },
          areaStyle: { color: style.color, opacity: 0.1 }
        }
      })
    }
  ]
}))
</script>
