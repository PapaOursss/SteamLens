<template>
  <div class="trends-page">
    <header class="page-header">
      <h1 class="title">Intérêt géographique & Propagation (Google Trends)</h1>
      <p class="subtitle">
        Visualisation de l'intérêt relatif (0 à 100) pour un jeu Steam ou un grand genre à travers le monde.
      </p>
    </header>

    <section class="selection-section">
      <div class="mode-switch">
        <button
          type="button"
          :class="['tab-btn', { active: mode === 'game' }]"
          @click="switchMode('game')"
        >
          Par jeu Steam
        </button>
        <button
          type="button"
          :class="['tab-btn', { active: mode === 'genre' }]"
          @click="switchMode('genre')"
        >
          Par genre
        </button>
      </div>

      <div v-if="mode === 'game'" class="selector-box">
        <GameSelector @select="onGameSelect" />
        <span v-if="selectedGameName" class="selected-badge">Jeu sélectionné : <strong>{{ selectedGameName }}</strong></span>
      </div>

      <div v-else class="selector-box">
        <label for="genre-select" class="selector-label">Choisir un genre :</label>
        <select id="genre-select" v-model="selectedGenre" class="genre-select" @change="onGenreChange">
          <option value="Action">Action</option>
          <option value="Survival">Survie (Survival)</option>
          <option value="RPG">Jeu de rôle (RPG)</option>
          <option value="Strategy">Stratégie</option>
          <option value="Adventure">Aventure</option>
          <option value="Simulation">Simulation</option>
        </select>
      </div>
    </section>

    <div v-if="loading" class="state-msg">Chargement des données Google Trends…</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    <div v-else-if="!timeline.length" class="state-msg empty">
      <span>📈</span>
      <p>Aucune donnée Google Trends enregistrée pour cette sélection.</p>
    </div>

    <section v-else class="map-section">
      <TrendsTimelineMap
        :timeline="timeline"
        :current-index="currentIndex"
        :current-date="currentDate"
        :current-scores="currentScores"
        :is-playing="isPlaying"
        :country-names="countryNames"
        @toggle-play="togglePlay"
        @set-index="setIndex"
      />
    </section>

    <aside class="notice-box">
      <h3>ℹ️ Comment c'est calculé & limites de pytrends</h3>
      <p>
        Les données proviennent de <strong>Google Trends</strong> (intérêt par région indexé de 0 à 100).
        L'API non-officielle étant sujette à des restrictions de fréquence strictes (blocages 429),
        les résultats sont mis en cache et peuvent être complétés par des exports CSV périodiques.
        Ce score mesure la popularité relative des recherches web, pas le nombre exact de ventes Steam.
      </p>
    </aside>
  </div>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'

const mode = ref<'game' | 'genre'>('game')
const selectedAppid = ref<number | null>(null)
const selectedGameName = ref<string>('')
const selectedGenre = ref<string>('Survival')

const countryNames = ref<Record<string, string>>({})

const {
  timeline,
  currentIndex,
  currentDate,
  currentScores,
  isPlaying,
  loading,
  error,
  fetchTrends,
  togglePlay,
  setIndex,
} = useTrendsMap({
  appid: computed(() => (mode.value === 'game' ? selectedAppid.value : null)),
  genre: computed(() => (mode.value === 'genre' ? selectedGenre.value : '')),
})

function switchMode(newMode: 'game' | 'genre') {
  mode.value = newMode
  fetchTrends()
}

function onGameSelect(game: GameOption) {
  selectedAppid.value = game.appid
  selectedGameName.value = game.name
  fetchTrends()
}

function onGenreChange() {
  fetchTrends()
}

onMounted(async () => {
  try {
    const geo = await $fetch<{ features: Array<{ properties: { iso3: string; name: string } }> }>('/world-110m.json')
    const map: Record<string, string> = {}
    for (const f of geo.features) {
      if (f.properties.iso3 && f.properties.iso3 !== '-99') {
        map[f.properties.iso3] = f.properties.name
      }
    }
    countryNames.value = map
  } catch {
    // repli
  }
  fetchTrends()
})
</script>

<style scoped>
.trends-page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
}
.page-header { margin-bottom: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem; }
.title { font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.subtitle { color: #4b5563; margin: 0; }
.selection-section { margin-bottom: 2rem; }
.mode-switch { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tab-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
  cursor: pointer;
  font-weight: 600;
  color: #4b5563;
}
.tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}
.selector-box { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.selected-badge { font-size: 0.9rem; color: #374151; }
.genre-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  background: #ffffff;
}
.selector-label { font-size: 0.9rem; font-weight: 600; color: #374151; }
.state-msg { text-align: center; padding: 3rem 1.5rem; color: #6b7280; }
.state-msg.error { color: #dc2626; }
.state-msg.empty span { font-size: 2.5rem; display: block; margin-bottom: 0.5rem; }
.notice-box {
  margin-top: 3rem;
  background: #f8fafc;
  border-left: 4px solid #64748b;
  padding: 1rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  color: #475569;
}
.notice-box h3 { margin: 0 0 0.5rem 0; font-size: 0.95rem; color: #1e293b; }
.notice-box p { margin: 0; line-height: 1.5; }
</style>
