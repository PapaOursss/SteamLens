<template>
  <p v-if="hasError" class="bg-deep p-6">Les contours de la carte n'ont pas pu être chargés.</p>
  <template v-else>
    <div class="aspect-[3/2] w-full sm:aspect-[2/1]">
      <ChartFrame v-if="isReady" :option="option" label="Carte du genre le plus surreprésenté par pays" @click="onClick" />
    </div>
    <ul class="mt-3 flex flex-wrap gap-x-5 gap-y-2">
      <li v-for="(genre, index) in genres" :key="genre" class="flex items-center gap-2">
        <span class="h-3 w-3" :style="{ background: genreColor(index) }" aria-hidden="true" />{{ genre }}
      </li>
    </ul>
  </template>
</template>

<script setup lang="ts">
import type { CountryTaste } from '~/types'

interface MapParam {
  name: string
}

const GENRE_COLORS = ['#C98500', '#2E97D4', '#E0628F', '#3FB58A', '#9B7BE0', '#D96B3C', '#7FA83A', '#5C7CFA']

const props = defineProps<{ genres: string[]; countries: CountryTaste[] }>()
const emit = defineEmits<{ select: [iso3: string] }>()

const { isReady, hasError } = useWorldMap()
const byIso3 = computed(() => new Map(props.countries.map((country) => [country.iso3, country])))

function genreColor(index: number): string {
  return GENRE_COLORS[index % GENRE_COLORS.length]!
}

function tooltipText(params: MapParam): string {
  const country = byIso3.value.get(params.name)
  const name = escapeHtml(countryName(params.name))
  return country ? `${name}<br><strong>${escapeHtml(country.dominant)}</strong>` : `${name}<br>Langue non suivie`
}

function onClick(params: MapParam) {
  if (byIso3.value.has(params.name)) emit('select', params.name)
}

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, trigger: 'item', formatter: tooltipText },
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
      data: props.countries.map((country) => ({
        name: country.iso3,
        value: country.reviews,
        itemStyle: { areaColor: genreColor(props.genres.indexOf(country.dominant)) }
      })),
      itemStyle: { areaColor: NO_DATA_COLOR, borderColor: COLORS.ground, borderWidth: 0.5 },
      emphasis: { label: { show: false }, itemStyle: { areaColor: COLORS.hot } },
      select: { disabled: true }
    }
  ]
}))
</script>
