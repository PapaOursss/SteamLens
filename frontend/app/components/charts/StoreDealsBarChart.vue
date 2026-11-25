<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="text-sm text-soft">
        <span v-if="comparison.steam_is_cheapest" class="font-semibold text-hot">
          Steam propose le meilleur prix !
        </span>
        <span v-else-if="comparison.cheapest_store" class="font-semibold text-hot">
          Moins cher sur {{ comparison.cheapest_store }} ({{ comparison.cheapest_price?.toFixed(2) }} $)
        </span>
      </div>
      <div v-if="comparison.steam_price !== null" class="text-sm">
        Prix Steam : <span class="font-mono font-bold">{{ comparison.steam_price.toFixed(2) }} $</span>
      </div>
    </div>

    <ChartFrame :option="chartOptions" :height="Math.max(220, comparison.deals.length * 36)" :label="label" />

    <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
      <a
        v-for="deal in comparison.deals"
        :key="deal.deal_id"
        :href="deal.redirect_url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex items-center justify-between rounded-md border border-line bg-raised p-2 text-sm transition hover:border-hot"
      >
        <div class="flex items-center gap-2 truncate">
          <img v-if="deal.store_icon" :src="deal.store_icon" :alt="deal.store_name" class="h-4 w-4 shrink-0" />
          <span class="truncate" :class="{ 'font-semibold text-hot': deal.is_steam }">{{ deal.store_name }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="deal.cut_percent > 0" class="rounded bg-hot/20 px-1 text-xs text-hot font-bold">
            -{{ deal.cut_percent }}%
          </span>
          <span class="font-mono font-bold">{{ deal.price.toFixed(2) }} $</span>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts'

export interface DealItem {
  store_id: string
  store_name: string
  store_icon: string
  deal_id: string
  price: number
  regular_price: number
  cut_percent: number
  is_steam: boolean
  redirect_url: string
}

export interface StoreComparison {
  appid: number
  steam_price: number | null
  cheapest_price: number | null
  cheapest_store: string | null
  steam_is_cheapest: boolean
  stores_count: number
  deals: DealItem[]
}

const props = defineProps<{
  comparison: StoreComparison
  label: string
}>()

const chartOptions = computed<EChartsOption>(() => {
  const deals = [...props.comparison.deals].reverse()
  const stores = deals.map((d) => d.store_name)
  const prices = deals.map((d) => ({
    value: d.price,
    itemStyle: {
      color: d.is_steam ? SERIES_COLORS[0] : (d.price === props.comparison.cheapest_price ? SERIES_COLORS[1] : COLORS.line)
    }
  }))

  return {
    ...chartBase(),
    tooltip: {
      ...chartBase().tooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `<b>${item.name}</b>: ${item.value} $`
      }
    },
    grid: { top: 10, right: 30, bottom: 20, left: 120 },
    xAxis: {
      type: 'value',
      axisLabel: { formatter: '{value} $' }
    },
    yAxis: {
      type: 'category',
      data: stores,
      axisLabel: { width: 100, overflow: 'truncate' }
    },
    series: [
      {
        type: 'bar',
        data: prices,
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => `${params.value} $`
        }
      }
    ]
  }
})
</script>
