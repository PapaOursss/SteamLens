<template>
  <div class="space-y-4">
    <p class="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
      <strong v-if="verdict" class="font-semibold">{{ verdict }}</strong>
      <span v-if="comparison.steam_price !== null" class="text-soft">
        Prix Steam : <strong class="figure text-text">{{ usd(comparison.steam_price) }}</strong>
      </span>
    </p>

    <ChartFrame :option="chartOptions" :height="chartHeight" :label="label" />

    <ul class="grid gap-px sm:grid-cols-2 lg:grid-cols-3">
      <li v-for="deal in comparison.deals" :key="deal.deal_id">
        <a
          :href="deal.redirect_url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex min-h-11 items-center justify-between gap-3 bg-deep px-3 hover:bg-raised"
        >
          <span class="flex min-w-0 items-center gap-2">
            <img v-if="deal.store_icon" :src="deal.store_icon" alt="" width="16" height="16" class="h-4 w-4 shrink-0">
            <span class="truncate" :class="{ 'font-semibold': deal.is_steam }">{{ deal.store_name }}</span>
          </span>
          <span class="figure flex shrink-0 items-center gap-2">
            <span v-if="deal.cut_percent > 0" class="bg-hot px-1 text-sm font-bold text-deep">−{{ deal.cut_percent }} %</span>
            <strong>{{ usd(deal.price) }}</strong>
            <span class="sr-only">(nouvel onglet)</span>
          </span>
        </a>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { StoreComparison } from '~/types'

const BAR_HEIGHT = 36
const MIN_HEIGHT = 160
const AXIS_ROOM = 40
const BAR_RADIUS = [0, 4, 4, 0]

const props = defineProps<{
  comparison: StoreComparison
  label: string
}>()

function usd(value: number): string {
  return formatAmount(value, 'USD')
}

const verdict = computed(() => {
  const { steam_is_cheapest: steamIsCheapest, cheapest_store: store, cheapest_price: price } = props.comparison
  if (steamIsCheapest) return 'Steam est au prix le plus bas.'
  if (store && price !== null) return `Moins cher sur ${store} : ${usd(price)}.`
  return ''
})

const chartHeight = computed(() => Math.max(MIN_HEIGHT, props.comparison.deals.length * BAR_HEIGHT + AXIS_ROOM))

/** Steam en couleur d'accent, le moins cher des autres en première série, le reste neutre. */
function barColor(price: number, isSteam: boolean): string {
  if (isSteam) return COLORS.hot
  return price === props.comparison.cheapest_price ? seriesColor(0) : COLORS.line
}

const chartOptions = computed(() => {
  const deals = [...props.comparison.deals].reverse()
  return {
    ...chartBase(),
    tooltip: {
      ...chartBase().tooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: { name: string; value: number }[]) =>
        `<strong>${escapeHtml(params[0]?.name ?? '')}</strong> : ${usd(params[0]?.value ?? 0)}`
    },
    grid: { top: 8, right: 88, bottom: 24, left: 8, containLabel: true },
    xAxis: { type: 'value', ...axisStyle(), axisLabel: { color: COLORS.soft, formatter: (value: number) => usd(value) } },
    yAxis: {
      type: 'category',
      data: deals.map((deal) => deal.store_name),
      ...axisStyle(),
      axisLabel: { color: COLORS.text, width: 120, overflow: 'truncate' }
    },
    series: [
      {
        type: 'bar',
        barMaxWidth: 24,
        data: deals.map((deal) => ({
          value: deal.price,
          itemStyle: { color: barColor(deal.price, deal.is_steam), borderRadius: BAR_RADIUS }
        })),
        label: {
          show: true,
          position: 'right',
          color: COLORS.text,
          fontFamily: FONT_BODY,
          formatter: (params: { value: number }) => usd(params.value)
        }
      }
    ]
  }
})
</script>
