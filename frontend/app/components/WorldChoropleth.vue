<template>
  <div class="map-wrapper">
    <ClientOnly>
      <VChart
        v-if="registered"
        class="chart"
        :option="option"
        autoresize
      />
      <template #fallback>
        <div class="placeholder">Chargement de la carte…</div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { registerMap } from 'echarts/core'
import type { CountryPrice } from '~/composables/useGamePriceMap'

const props = defineProps<{
  prices: CountryPrice[]
  countryNames: Record<string, string>
}>()

const registered = ref(false)

onMounted(async () => {
  const geo = await $fetch<object>('/world-110m.json')
  registerMap('world', geo as Parameters<typeof registerMap>[1])
  registered.value = true
})

const mapData = computed(() =>
  props.prices
    .filter((p) => p.price_eur > 0)
    .map((p) => ({ name: props.countryNames[p.iso3] ?? p.iso3, value: p.price_eur }))
)

const maxPrice = computed(() =>
  mapData.value.length ? Math.max(...mapData.value.map((d) => d.value)) : 60
)

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: { name: string; value: number | undefined }) =>
      params.value !== undefined
        ? `${params.name}<br/>${params.value.toFixed(2)} €`
        : params.name,
  },
  visualMap: {
    min: 0,
    max: maxPrice.value,
    left: 'left',
    bottom: '5%',
    text: ['Cher', 'Pas cher'],
    inRange: { color: ['#bbf7d0', '#065f46'] },
    calculable: true,
  },
  series: [
    {
      type: 'map',
      map: 'world',
      roam: true,
      emphasis: { label: { show: false } },
      data: mapData.value,
    },
  ],
}))
</script>

<style scoped>
.map-wrapper { width: 100%; background: #f8fafc; border-radius: 0.75rem; overflow: hidden; }
.chart { width: 100%; height: 480px; }
.placeholder { height: 480px; display: flex; align-items: center; justify-content: center; color: #6b7280; }
</style>
