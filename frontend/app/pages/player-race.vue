<template>
  <div>
    <PageIntro title="Course des jeux les plus joués" is-lab>
      L'évolution des jeux les plus fréquentés sur Steam mois par mois depuis 2012 (bar chart race et bump chart).
    </PageIntro>

    <DataBlock
      title="Course au fil des mois"
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!months.length"
      empty-message="Pas encore de données d'historique de joueurs."
      :height="560"
      @retry="refresh()"
    >
      <template #actions>
        <SegmentedControl v-model="viewMode" :options="VIEW_OPTIONS" label="Vue" />
      </template>

      <div v-if="viewMode === 'race'" class="space-y-4">
        <div class="flex flex-wrap items-center gap-4">
          <button type="button" class="button" :disabled="months.length < 2" @click="togglePlay">
            {{ isPlaying ? 'Pause' : 'Lecture animée' }}
          </button>
          <label class="flex min-w-48 flex-1 flex-col">
            <span class="text-soft">Mois : <strong class="figure text-text">{{ currentMonth }}</strong></span>
            <input
              type="range"
              min="0"
              :max="Math.max(0, months.length - 1)"
              :value="currentIndex"
              class="min-h-11 w-full accent-hot"
              @input="setIndex(Number(($event.target as HTMLInputElement).value))"
            >
          </label>
        </div>

        <BarChartRace
          :entries="currentEntries"
          :current-month="currentMonth"
          :height="460"
          label="Course des jeux les plus joués par mois"
        />
      </div>

      <div v-else>
        <p class="mb-4 text-sm text-soft">
          Trajectoire et variations de rang des jeux majeurs à travers le temps.
        </p>
        <BumpChart
          :months="months"
          :timeline="data?.timeline || {}"
          :height="480"
          label="Classement des jeux dans le temps (bump chart)"
        />
      </div>
    </DataBlock>

    <p class="gutter max-w-prose text-soft">
      Données issues des relevés historiques SteamCharts et snapshots de joueurs connectés Steam.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption } from '~/types'

type ViewMode = 'race' | 'bump'

const VIEW_OPTIONS: ChoiceOption<ViewMode>[] = [
  { value: 'race', label: 'Bar Chart Race' },
  { value: 'bump', label: 'Bump Chart' }
]

useHead({ title: 'Course des jeux' })

const viewMode = ref<ViewMode>('race')

const {
  data,
  isLoading,
  hasError,
  refresh,
  months,
  currentIndex,
  currentMonth,
  currentEntries,
  isPlaying,
  togglePlay,
  setIndex,
} = usePlayerRace()
</script>
