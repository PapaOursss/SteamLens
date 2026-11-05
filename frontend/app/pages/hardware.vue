<template>
  <div>
    <PageIntro title="Qui sont les joueurs Steam ?" is-lab>
      L'enquête matériel et logiciels de Steam, mois après mois : langues, systèmes, cartes graphiques, mémoire et casques VR.
    </PageIntro>

    <div v-if="survey?.highlights.length" class="gutter grid gap-x-8 gap-y-4 md:grid-cols-3">
      <StatTile
        v-for="highlight in survey.highlights"
        :key="highlight.label"
        :label="highlight.label"
        :value="latestValue(highlight.values)"
        :hint="lastMonth"
      />
    </div>

    <DataBlock
      title="Part des joueurs interrogés"
      note="Les éléments les plus répandus au dernier mois connu. Chaque courbe a sa propre échelle."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!survey?.months.length"
      empty-message="Pas encore de données : l'import de l'enquête n'a pas tourné sur cette base."
      @retry="refresh()"
    >
      <template #actions>
        <SegmentedControl v-model="category" :options="CATEGORIES" label="Catégorie" />
      </template>
      <SurveyMultiples v-if="survey" :months="survey.months" :series="survey.series" />
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption, HardwareSurvey } from '~/types'

type Category = 'language' | 'os' | 'gpu' | 'ram' | 'vr'

const CATEGORIES: ChoiceOption<Category>[] = [
  { value: 'language', label: 'Langues' },
  { value: 'os', label: 'Systèmes' },
  { value: 'gpu', label: 'Cartes graphiques' },
  { value: 'ram', label: 'Mémoire' },
  { value: 'vr', label: 'Casques VR' }
]
const MONTH_LENGTH = 7

useHead({ title: 'Matériel des joueurs' })

const category = ref<Category>('language')
const { data: survey, isLoading, hasError, refresh } = useApiResource<HardwareSurvey>(
  '/stats/hardware-survey/',
  () => ({ category: category.value })
)

const lastMonth = computed(() => survey.value?.months.at(-1)?.slice(0, MONTH_LENGTH))

function latestValue(values: (number | null)[]): string {
  const value = values.findLast((entry) => entry !== null)
  return value === undefined || value === null ? '—' : formatPercent(value)
}
</script>
