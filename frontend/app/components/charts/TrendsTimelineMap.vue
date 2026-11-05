<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center gap-4">
      <button type="button" class="button" :disabled="timeline.length < 2" @click="$emit('togglePlay')">
        {{ isPlaying ? 'Pause' : 'Lecture' }}
      </button>
      <label class="flex min-w-48 flex-1 flex-col">
        <span class="text-soft">Date : <strong class="figure text-text">{{ formatDate(currentDate) }}</strong></span>
        <input
          type="range"
          min="0"
          :max="timeline.length - 1"
          :value="currentIndex"
          class="min-h-11 w-full accent-hot"
          @input="$emit('setIndex', Number(($event.target as HTMLInputElement).value))"
        >
      </label>
    </div>
    <WorldValueMap :values="values" :scale="SCALE" :format-value="formatScore" label="Carte de l'intérêt Google Trends par pays" />
    <div class="mt-8 max-w-3xl"><RankBars :rows="rows" :maximum="SCALE.max" /></div>
  </div>
</template>

<script setup lang="ts">
import type { RankRow } from '~/types'

const SCALE = { min: 0, max: 100 }
const LISTED_COUNTRIES = 15

const props = defineProps<{
  timeline: string[]
  currentIndex: number
  currentDate: string
  currentScores: Record<string, number>
  isPlaying: boolean
}>()

defineEmits<{ togglePlay: []; setIndex: [index: number] }>()

function formatScore(score: number): string {
  return `${score} / ${SCALE.max}`
}

const values = computed(() =>
  Object.entries(props.currentScores).map(([iso3, value]) => ({ iso3, value }))
)

const rows = computed<RankRow[]>(() =>
  [...values.value]
    .sort((first, second) => second.value - first.value)
    .slice(0, LISTED_COUNTRIES)
    .map(({ iso3, value }) => ({ key: iso3, label: countryName(iso3), value, display: formatScore(value) }))
)
</script>
