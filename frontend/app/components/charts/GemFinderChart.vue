<template>
  <ChartFrame :option="option" :height="height" :label="label" @click="handleChartClick" />
</template>

<script setup lang="ts">
import type { GemCriteria, GemFinderGame } from '~/types'

const MIN_SYMBOL_SIZE = 4
const MAX_SYMBOL_SIZE = 20
const MIN_LOG_OWNERS = 3
const LOG_OWNERS_RANGE = 4.5
const OTHER_OPACITY = 0.45
const GEM_OPACITY = 0.9
const ZONE_OPACITY = 0.12
const PERCENT = 100

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

/** Aire du point selon les possesseurs, en échelle log (de mille à trente millions). */
function symbolSize(owners: number): number {
  const position = (Math.log10(Math.max(owners, 1)) - MIN_LOG_OWNERS) / LOG_OWNERS_RANGE
  const clamped = Math.min(1, Math.max(0, position))
  return Math.round(MIN_SYMBOL_SIZE + clamped * (MAX_SYMBOL_SIZE - MIN_SYMBOL_SIZE))
}

function handleChartClick(params: { data?: { game?: GemFinderGame } }) {
  if (params?.data?.game) emit('select', params.data.game)
}

function tooltipFormatter(param: { data: { game: GemFinderGame } }): string {
  const game = param.data.game
  const price = game.price_eur > 0 ? formatPrice(game.price_eur) : 'Gratuit'
  const gem = game.is_gem ? ' · pépite' : ''
  return `<strong>${escapeHtml(game.name)}</strong>${gem}<br>`
    + `${price} · ${formatPercent(game.positive_percent)} d'avis positifs<br>`
    + `${escapeHtml(game.genre)} · ~${formatCompact(game.owners)} possesseurs`
}

function points(games: GemFinderGame[]) {
  return games.map((game) => ({
    value: [game.price_eur, game.positive_percent],
    symbolSize: symbolSize(game.owners),
    game
  }))
}

const gemZone = computed(() => ({
  silent: true,
  // Sans étiquette : les points la couvriraient ; la règle est dite au-dessus du graphique.
  itemStyle: { color: COLORS.hot, opacity: ZONE_OPACITY },
  label: { show: false },
  data: [[{ coord: [0, props.criteria.min_score] }, { coord: [props.criteria.max_price, PERCENT] }]]
}))

const option = computed(() => ({
  ...chartBase(),
  legend: { top: 0, data: ['Pépites', 'Autres jeux'], textStyle: { color: COLORS.text, fontFamily: FONT_BODY } },
  grid: { left: 56, right: 24, top: 48, bottom: 48 },
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltipFormatter },
  xAxis: {
    type: 'value',
    name: 'Prix',
    nameLocation: 'middle',
    nameGap: 30,
    ...axisStyle(),
    axisLabel: { color: COLORS.soft, formatter: (value: number) => formatPrice(value) }
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: PERCENT,
    name: "Avis positifs",
    ...axisStyle(),
    axisLabel: { color: COLORS.soft, formatter: '{value} %' }
  },
  series: [
    {
      name: 'Autres jeux',
      type: 'scatter',
      itemStyle: { color: COLORS.line, opacity: OTHER_OPACITY },
      data: points(props.games.filter((game) => !game.is_gem)),
      markArea: gemZone.value
    },
    {
      name: 'Pépites',
      type: 'scatter',
      itemStyle: { color: COLORS.hot, opacity: GEM_OPACITY, borderColor: COLORS.deep, borderWidth: 1 },
      data: points(props.games.filter((game) => game.is_gem))
    }
  ]
}))
</script>
