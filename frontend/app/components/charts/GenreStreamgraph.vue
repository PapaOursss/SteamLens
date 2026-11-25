<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { StreamgraphEvent } from '~/types'


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

/** En dessous, une année est un bruit de fond (quelques sorties avant l'ouverture de Steam). */
const MIN_SHARE_OF_PEAK = 0.01

/**
 * Années montrées : depuis la première qui compte vraiment, jusqu'à la dernière complète.
 * L'année en cours n'est pas finie : la courbe s'y effondrerait sans raison.
 */
const shownYears = computed(() => {
  const totals = props.years.map((_, index) => props.series.reduce((sum, counts) => sum + (counts[index] ?? 0), 0))
  const threshold = Math.max(...totals, 0) * MIN_SHARE_OF_PEAK
  const first = totals.findIndex((total) => total >= threshold)
  const currentYear = new Date().getFullYear()
  return props.years
    .map((year, index) => ({ year, index }))
    .filter(({ year, index }) => index >= first && year < currentYear)
})

const option = computed(() => {
  const data: [string, number, string][] = []
  props.genres.forEach((genre, genreIdx) => {
    const genreCounts = props.series[genreIdx] ?? []
    for (const { year, index } of shownYears.value) {
      data.push([`${year}/01/01`, genreCounts[index] ?? 0, genre])
    }
  })

  return {
    ...chartBase(),
    color: [...SERIES_COLORS],
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
            borderColor: COLORS.text,
            borderWidth: 1
          }
        },
        data
      }
    ]
  }
})
</script>
