<template>
  <p v-if="hasError" class="bg-deep p-6">Les contours de la carte n'ont pas pu être chargés.</p>
  <div v-else class="aspect-[3/2] w-full sm:aspect-[2/1]">
    <ChartFrame v-if="isReady" :option="option" :label="label" />
  </div>
  <p v-if="!hasError" class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
    <span class="figure">{{ formatPrice(bounds.min) }}</span>
    <span class="h-3 w-36 rounded-sm" :style="{ background: LEGEND_GRADIENT }" aria-hidden="true" />
    <span class="figure">{{ formatPrice(bounds.max) }}</span>
    <span class="ml-3 flex items-center gap-2 text-soft">
      <span class="h-3 w-6 rounded-sm bg-deep" aria-hidden="true" />
      Pas de relevé
    </span>
  </p>
</template>

<script setup lang="ts">
import type { CountryValue } from '~/types'

const LEGEND_GRADIENT = `linear-gradient(to right, ${SEQUENTIAL_COLORS.join(', ')})`

interface MapTooltipParam {
  name: string
  value: number
}

const props = defineProps<{ values: CountryValue[]; label: string }>()

const { isReady, hasError } = useWorldMap()

const bounds = computed(() => {
  const numbers = props.values.map((entry) => entry.value)
  return { min: Math.min(...numbers), max: Math.max(...numbers) }
})

function tooltipText(params: MapTooltipParam): string {
  const name = escapeHtml(countryName(params.name))
  return Number.isFinite(params.value)
    ? `${name}<br><strong>${formatPrice(params.value)}</strong>`
    : `${name}<br>Pas de relevé`
}

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltipText },
  visualMap: {
    ...bounds.value,
    show: false,
    inRange: { color: [...SEQUENTIAL_COLORS] }
  },
  series: [
    {
      type: 'map',
      map: WORLD_MAP_NAME,
      nameProperty: 'iso3',
      roam: false,
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
      data: props.values.map((entry) => ({ name: entry.iso3, value: entry.value })),
      itemStyle: { areaColor: NO_DATA_COLOR, borderColor: COLORS.ground, borderWidth: 0.5 },
      emphasis: { label: { show: false }, itemStyle: { areaColor: COLORS.hot } },
      select: { disabled: true }
    }
  ]
}))
</script>
