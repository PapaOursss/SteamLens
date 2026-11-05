<template>
  <p v-if="hasError" class="bg-deep p-6">Les contours de la carte n'ont pas pu être chargés.</p>
  <div v-else class="aspect-[3/2] w-full sm:aspect-[2/1]">
    <ChartFrame v-if="isReady" :option="option" :label="label" />
  </div>
  <ScaleLegend v-if="!hasError" :low="formatValue(bounds.min)" :high="formatValue(bounds.max)" no-data-label="Pas de relevé" />
</template>

<script setup lang="ts">
import type { CountryValue } from '~/types'

interface MapTooltipParam {
  name: string
  value: number
}

/** `scale` : échelle fixe, pour qu'une carte animée garde ses couleurs d'une date à l'autre. */
const props = withDefaults(
  defineProps<{
    values: CountryValue[]
    label: string
    formatValue?: (value: number) => string
    scale?: { min: number; max: number }
  }>(),
  { formatValue: formatPrice, scale: undefined }
)

const { isReady, hasError } = useWorldMap()

const bounds = computed(() => {
  if (props.scale) return props.scale
  const numbers = props.values.map((entry) => entry.value)
  return { min: Math.min(...numbers), max: Math.max(...numbers) }
})

function tooltipText(params: MapTooltipParam): string {
  const name = escapeHtml(countryName(params.name))
  return Number.isFinite(params.value)
    ? `${name}<br><strong>${props.formatValue(params.value)}</strong>`
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
