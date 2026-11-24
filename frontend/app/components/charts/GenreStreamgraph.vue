<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { StreamgraphEvent } from '~/types'

const PALETTE = [
  '#FFC53D',
  '#2E97D4',
  '#E0628F',
  '#6EE7B7',
  '#F472B6',
  '#60A5FA',
  '#FBBF24',
  '#A78BFA'
]

const props = withDefaults(
  defineProps<{
    years: number[]
    genres: string[]
    series: number[][]
    events?: StreamgraphEvent[]
    height?: number
    label: string
  }>(),
  {
    height: 440,
    events: () => []
  }
)

interface TooltipParam {
  value: [string, number, string]
  color: string
}

function tooltipFormatter(params: TooltipParam): string {
  const [dateStr, count, genre] = params.value
  const year = dateStr.slice(0, 4)
  const escapedGenre = escapeHtml(genre)
  return `<strong>${escapedGenre}</strong> (${year})<br>${formatNumber(count)} sorties`
}

const option = computed(() => {
  const data: [string, number, string][] = []
  props.genres.forEach((genre, genreIdx) => {
    const genreCounts = props.series[genreIdx] || []
    props.years.forEach((year, yearIdx) => {
      const count = genreCounts[yearIdx] ?? 0
      data.push([`${year}/01/01`, count, genre])
    })
  })

  return {
    ...chartBase(),
    color: PALETTE,
    tooltip: {
      ...chartBase().tooltip,
      trigger: 'item',
      formatter: tooltipFormatter
    },
    legend: {
      data: props.genres,
      top: 0,
      textStyle: { color: COLORS.soft, fontFamily: FONT_BODY }
    },
    singleAxis: {
      top: 50,
      bottom: 50,
      axisTick: {},
      axisLabel: { color: COLORS.soft },
      type: 'time',
      axisPointer: {
        animation: true,
        label: {
          show: true,
          formatter: (params: { value: string | number }) => {
            const date = new Date(params.value)
            return isNaN(date.getFullYear()) ? String(params.value) : String(date.getFullYear())
          }
        }
      },
      splitLine: {
        show: true,
        lineStyle: { color: COLORS.raised, type: 'dashed' }
      }
    },
    series: [
      {
        type: 'themeRiver',
        // La légende nomme déjà les genres : à gauche, leurs noms se superposent.
        label: { show: false },
        emphasis: {
          itemStyle: {
            shadowBlur: 15,
            shadowColor: 'rgba(0, 0, 0, 0.6)'
          }
        },
        data
      }
    ]
  }
})
</script>
