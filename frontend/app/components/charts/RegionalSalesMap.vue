<template>
  <div class="grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-start">
    <div>
      <SegmentedControl v-model="selected" :options="options" label="Marché affiché" class="mb-4" />
      <svg viewBox="0 0 1000 500" class="block h-auto w-full bg-deep" role="img" :aria-label="`Carte des quatre marchés, ${active.label} en avant`">
        <g
          v-for="zone in ZONES"
          :key="zone.key"
          class="cursor-pointer"
          @click="selected = zone.key"
        >
          <path
            v-for="shape in zone.shapes"
            :key="shape"
            :d="shape"
            :fill="colorOf(zone.key)"
            :fill-opacity="zone.key === selected ? 1 : 0.4"
            :stroke="zone.key === selected ? COLORS.text : COLORS.deep"
            stroke-width="2"
            stroke-linejoin="round"
          />
          <text
            v-for="name in zone.labels"
            :key="name.text"
            :x="name.x"
            :y="name.y"
            :fill="COLORS.text"
            text-anchor="middle"
            font-size="16"
            font-weight="700"
            class="pointer-events-none"
          >
            {{ name.text }}
          </text>
        </g>
      </svg>
    </div>

    <div>
      <p class="text-soft">{{ active.area }}</p>
      <h3 class="mt-1 text-3xl">{{ active.label }}</h3>
      <p class="mt-4 font-display text-5xl font-extrabold text-hot figure">{{ formatNumber(round(total)) }} M</p>
      <p class="text-soft">exemplaires vendus, {{ formatPercent(round(share)) }} des ventes mondiales</p>
      <p class="mt-4 max-w-prose leading-relaxed">{{ active.description }}</p>

      <h4 class="mt-6 font-display text-lg font-bold">Ses trois genres en tête</h4>
      <ul class="mt-2 space-y-3">
        <li v-for="row in topGenres" :key="row.genre">
          <div class="flex justify-between gap-4">
            <span>{{ row.genre }}</span>
            <span class="text-soft figure">{{ formatNumber(row.volume) }} M</span>
          </div>
          <div class="mt-1 h-2 bg-deep">
            <div class="h-full" :style="{ width: `${(row.volume / topGenres[0]!.volume) * 100}%`, backgroundColor: active.color }" />
          </div>
        </li>
      </ul>

      <h4 class="mt-6 font-display text-lg font-bold">Ses succès emblématiques</h4>
      <p class="mt-2 text-soft">{{ active.hits.join(' · ') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption, RegionalGenreSales, SalesRegionKey } from '~/types'

/** Formes simplifiées des continents, dessinées à la main sur une grille de 1000 × 500. */
const ZONES: { key: SalesRegionKey; shapes: string[]; labels: { text: string; x: number; y: number }[] }[] = [
  {
    key: 'na',
    shapes: [
      'M 120 70 L 220 50 L 310 60 L 340 100 L 290 140 L 210 130 L 170 150 L 110 120 Z',
      'M 150 150 L 290 140 L 320 180 L 290 230 L 200 230 L 160 200 Z',
      'M 180 230 L 250 230 L 230 290 L 190 270 Z'
    ],
    labels: [{ text: 'Amérique du Nord', x: 225, y: 180 }]
  },
  {
    key: 'eu',
    shapes: [
      'M 520 60 L 550 50 L 570 90 L 540 130 L 520 100 Z',
      'M 460 110 L 485 105 L 480 140 L 460 130 Z',
      'M 470 140 L 550 125 L 610 130 L 600 190 L 550 210 L 480 210 L 465 170 Z'
    ],
    labels: [{ text: 'Europe', x: 535, y: 172 }]
  },
  {
    key: 'jp',
    shapes: ['M 850 160 L 870 170 L 885 200 L 860 220 L 840 210 L 845 180 Z'],
    labels: [{ text: 'Japon', x: 862, y: 148 }]
  },
  {
    key: 'other',
    shapes: [
      'M 270 290 L 340 310 L 370 370 L 330 460 L 290 420 L 260 340 Z',
      'M 470 220 L 570 220 L 600 290 L 570 390 L 520 410 L 480 320 Z',
      'M 610 120 L 820 110 L 840 200 L 760 290 L 670 270 L 610 200 Z',
      'M 780 340 L 880 330 L 890 410 L 800 420 Z'
    ],
    labels: [
      { text: 'Amérique du Sud', x: 315, y: 380 },
      { text: 'Afrique', x: 530, y: 320 },
      { text: 'Asie', x: 720, y: 200 },
      { text: 'Océanie', x: 835, y: 380 }
    ]
  }
]

const props = defineProps<{ sales: RegionalGenreSales[] }>()

const selected = ref<SalesRegionKey>('jp')

const options: ChoiceOption<SalesRegionKey>[] = SALES_REGIONS.map((region) => ({ value: region.key, label: region.label }))

const active = computed(() => SALES_REGIONS.find((region) => region.key === selected.value)!)
const total = computed(() => regionTotal(props.sales, selected.value))
const share = computed(() => {
  const world = props.sales.reduce((sum, row) => sum + worldTotal(row), 0)
  return world ? (total.value / world) * 100 : 0
})
const topGenres = computed(() =>
  props.sales
    .map((row) => ({ genre: row.genre, volume: row[selected.value] }))
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 3)
)

function colorOf(key: SalesRegionKey): string {
  return SALES_REGIONS.find((region) => region.key === key)!.color
}

function round(value: number): number {
  return Math.round(value * 10) / 10
}
</script>
