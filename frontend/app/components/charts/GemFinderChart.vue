<template>
  <ChartFrame :option="option" :height="height" :label="label" @click="handleChartClick" />
</template>

<script setup lang="ts">
import type { GemCriteria, GemFinderGame } from '~/types'

const MIN_SYMBOL_SIZE = 8
const MAX_SYMBOL_SIZE = 34
const LOG_BASE = 10

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
    games: GemFinderGame[]
    criteria: GemCriteria
    height?: number
    label: string
  }>(),
  { height: 500 }
)

const emit = defineEmits<{
  select: [game: GemFinderGame]
}>()

function calculateSymbolSize(owners: number): number {
  const safeOwners = Math.max(1000, owners)
  const logVal = Math.log10(safeOwners)
  const normalized = Math.max(0, Math.min(1, (logVal - 3) / 4.5))
  return Math.round(MIN_SYMBOL_SIZE + normalized * (MAX_SYMBOL_SIZE - MIN_SYMBOL_SIZE))
}

function handleChartClick(params: { data?: { game?: GemFinderGame } }) {
  if (params?.data?.game) {
    emit('select', params.data.game)
  }
}

interface TooltipParam {
  data: {
    value: [number, number]
    game: GemFinderGame
  }
}

function tooltipFormatter(param: TooltipParam): string {
  const g = param.data.game
  const title = escapeHtml(g.name)
  const price = g.price_eur > 0 ? `${g.price_eur} €` : 'Gratuit'
  const tag = g.is_gem ? ' <span style="color: #FFC53D; font-weight: bold;">(Pépite !)</span>' : ''
  return `<strong>${title}</strong>${tag}<br>` +
    `Prix : ${price}<br>` +
    `Avis positifs : <strong>${g.positive_percent} %</strong><br>` +
    `Genre : ${escapeHtml(g.genre)}<br>` +
    `Propriétaires : ~${formatCompactNumber(g.owners)}`
}

const option = computed(() => {
  const genres = Array.from(new Set(props.games.map((g) => g.genre))).sort()
  const genreColorMap = new Map<string, string>()
  genres.forEach((genre, idx) => {
    genreColorMap.set(genre, PALETTE[idx % PALETTE.length]!)
  })

  const seriesList = genres.map((genre) => {
    const genreGames = props.games.filter((g) => g.genre === genre)
    return {
      name: genre,
      type: 'scatter',
      itemStyle: {
        color: genreColorMap.get(genre),
        opacity: 0.85
      },
      data: genreGames.map((g) => ({
        value: [g.price_eur, g.positive_percent],
        symbolSize: calculateSymbolSize(g.owners),
        game: g
      }))
    }
  })

  return {
    ...chartBase(),
    legend: {
      data: genres,
      top: 0,
      textStyle: { color: COLORS.soft, fontFamily: FONT_BODY }
    },
    grid: { left: 50, right: 30, top: 40, bottom: 45 },
    tooltip: {
      ...chartBase().tooltip,
      trigger: 'item',
      formatter: tooltipFormatter
    },
    xAxis: {
      type: 'value',
      name: 'Prix (€)',
      nameLocation: 'middle',
      nameGap: 28,
      nameTextStyle: { color: COLORS.soft },
      ...axisStyle(),
      splitLine: { lineStyle: { color: COLORS.raised, type: 'dashed' } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      name: '% Avis positifs',
      nameTextStyle: { color: COLORS.soft },
      ...axisStyle(),
      axisLabel: { color: COLORS.soft, formatter: '{value} %' },
      splitLine: { lineStyle: { color: COLORS.raised, type: 'dashed' } }
    },
    series: [
      ...seriesList,
      {
        type: 'scatter',
        data: [],
        markArea: {
          silent: true,
          itemStyle: {
            color: 'rgba(255, 197, 61, 0.12)',
            borderWidth: 1,
            borderColor: 'rgba(255, 197, 61, 0.4)',
            borderType: 'dashed'
          },
          label: {
            show: true,
            position: ['10', '10'],
            formatter: 'Zone « Pépites »\n(<= 15 €, >= 85 % avis)',
            color: COLORS.hot,
            fontSize: 11
          },
          data: [
            [
              { coord: [0, props.criteria.min_score] },
              { coord: [props.criteria.max_price, 100] }
            ]
          ]
        }
      }
    ]
  }
})
</script>
