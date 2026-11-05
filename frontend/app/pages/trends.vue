<template>
  <div>
    <PageIntro title="L'intérêt à travers le monde" is-lab>
      L'intérêt relatif pour un jeu ou un genre selon Google Trends, de 0 à 100. Il mesure la popularité des recherches web, pas les ventes.
    </PageIntro>

    <DataBlock
      title="Pays par pays, date après date"
      :is-loading="loading"
      :has-error="Boolean(error)"
      :is-empty="!timeline.length"
      empty-message="Pas encore de données Google Trends pour cette sélection."
      :height="520"
      @retry="fetchTrends()"
    >
      <template #actions>
        <div class="flex flex-wrap items-center gap-3">
          <SegmentedControl v-model="mode" :options="MODES" label="Regarder par" />
          <GameSearch v-if="mode === 'game'" field-id="recherche-trends" label="Jeu" class="w-full sm:w-80" @select="selectGame" />
          <SegmentedControl v-else v-model="genre" :options="GENRES" label="Genre" />
        </div>
      </template>
      <TrendsTimelineMap
        :timeline="timeline"
        :current-index="currentIndex"
        :current-date="currentDate"
        :current-scores="currentScores"
        :is-playing="isPlaying"
        @toggle-play="togglePlay"
        @set-index="setIndex"
      />
    </DataBlock>

    <p class="gutter max-w-prose text-soft">
      L'API non officielle de Google Trends limite vite les requêtes : les résultats sont gardés en cache et peuvent être complétés par des exports CSV.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption } from '~/types'

type Mode = 'game' | 'genre'

const MODES: ChoiceOption<Mode>[] = [
  { value: 'game', label: 'Jeu' },
  { value: 'genre', label: 'Genre' }
]
const GENRES: ChoiceOption<string>[] = [
  { value: 'Action', label: 'Action' },
  { value: 'Survival', label: 'Survie' },
  { value: 'RPG', label: 'Jeu de rôle' },
  { value: 'Strategy', label: 'Stratégie' },
  { value: 'Adventure', label: 'Aventure' },
  { value: 'Simulation', label: 'Simulation' }
]

useHead({ title: 'Google Trends' })

const { appid, selectGame } = useGameFromRoute()
const mode = ref<Mode>('game')
const genre = ref('Survival')

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
  setIndex
} = useTrendsMap({
  appid: computed(() => (mode.value === 'game' ? appid.value : null)),
  genre: computed(() => (mode.value === 'genre' ? genre.value : ''))
})

onMounted(fetchTrends)
watch([mode, genre, appid], fetchTrends)
</script>
