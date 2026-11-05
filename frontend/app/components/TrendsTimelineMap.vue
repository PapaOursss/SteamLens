<template>
  <div class="trends-map-container">
    <div class="controls-bar">
      <button class="btn-play" type="button" @click="$emit('togglePlay')">
        {{ isPlaying ? '⏸ Pause' : '▶ Lecture animée' }}
      </button>
      <div class="slider-wrapper">
        <label for="date-slider" class="slider-label">Date : <strong>{{ currentDate }}</strong></label>
        <input
          id="date-slider"
          type="range"
          min="0"
          :max="Math.max(0, timeline.length - 1)"
          :value="currentIndex"
          class="slider"
          @input="$emit('setIndex', Number(($event.target as HTMLInputElement).value))"
        />
      </div>
      <div class="date-badge">{{ currentDate || 'Aucune date' }}</div>
    </div>

    <div class="map-view">
      <div class="legend-scale">
        <span class="legend-label">Intérêt Google Trends (0 - 100)</span>
        <div class="legend-bar"></div>
        <div class="legend-ticks">
          <span>0 (Faible)</span>
          <span>50</span>
          <span>100 (Fort)</span>
        </div>
      </div>

      <div class="countries-grid">
        <div
          v-for="country in displayCountries"
          :key="country.iso3"
          class="country-card"
          :style="{ borderColor: getCountryColor(country.score) }"
        >
          <div class="country-header">
            <span class="country-name">{{ country.name }}</span>
            <span class="country-code">{{ country.iso3 }}</span>
          </div>
          <div class="country-bar-bg">
            <div
              class="country-bar-fill"
              :style="{
                width: `${country.score}%`,
                backgroundColor: getCountryColor(country.score),
              }"
            ></div>
          </div>
          <div class="country-score">
            <span>Score :</span>
            <strong>{{ country.score }} / 100</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  timeline: string[]
  currentIndex: number
  currentDate: string
  currentScores: Record<string, number>
  isPlaying: boolean
  countryNames: Record<string, string>
}>()

defineEmits<{
  (e: 'togglePlay'): void
  (e: 'setIndex', index: number): void
}>()

interface CountryDisplay {
  iso3: string
  name: string
  score: number
}

const displayCountries = computed<CountryDisplay[]>(() => {
  const entries = Object.entries(props.currentScores)
  return entries
    .map(([iso3, score]) => ({
      iso3,
      name: props.countryNames[iso3] ?? iso3,
      score,
    }))
    .sort((a, b) => b.score - a.score)
})

function getCountryColor(score: number): string {
  if (score >= 80) return '#ef4444' // rouge vif
  if (score >= 60) return '#f97316' // orange
  if (score >= 40) return '#eab308' // jaune
  if (score >= 20) return '#3b82f6' // bleu
  return '#94a3b8' // gris
}
</script>

<style scoped>
.trends-map-container {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.controls-bar {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.btn-play {
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-play:hover { background: #1d4ed8; }
.slider-wrapper { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 0.25rem; }
.slider-label { font-size: 0.85rem; color: #4b5563; }
.slider { width: 100%; cursor: pointer; }
.date-badge {
  background: #f3f4f6;
  padding: 0.4rem 0.8rem;
  border-radius: 0.375rem;
  font-weight: 700;
  color: #1f2937;
  font-size: 0.9rem;
}
.legend-scale { margin-bottom: 1.5rem; }
.legend-label { font-size: 0.85rem; font-weight: 600; color: #374151; display: block; margin-bottom: 0.3rem; }
.legend-bar {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #94a3b8, #3b82f6, #eab308, #f97316, #ef4444);
}
.legend-ticks { display: flex; justify-content: space-between; font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem; }
.countries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.country-card {
  border: 1px solid #e5e7eb;
  border-left-width: 4px;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f9fafb;
}
.country-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.4rem; }
.country-name { font-weight: 600; font-size: 0.9rem; color: #111827; }
.country-code { font-size: 0.75rem; color: #9ca3af; font-weight: 700; }
.country-bar-bg { height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; margin-bottom: 0.4rem; }
.country-bar-fill { height: 100%; transition: width 0.3s ease; }
.country-score { font-size: 0.8rem; color: #4b5563; display: flex; justify-content: space-between; }
</style>
