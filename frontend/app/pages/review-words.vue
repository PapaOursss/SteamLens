<template>
  <div>
    <PageIntro title="Les mots des avis" is-lab>
      Ce que les joueurs écrivent quand ils recommandent un jeu, et quand ils le déconseillent. Plus un mot est grand, plus il revient dans les avis.
    </PageIntro>

    <DataBlock
      :title="words?.name ?? 'Tous les jeux suivis'"
      note="Extraits d'avis de la boutique Steam et du jeu de données Kaggle (texte seul, sans auteur). Mots vides retirés ; un mot compte une fois par avis."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!words?.positive.words.length && !words?.negative.words.length"
      empty-message="Pas encore d'extraits d'avis dans cette langue pour cette sélection."
      :height="CLOUD_HEIGHT"
      @retry="refresh()"
    >
      <template #actions>
        <div class="flex flex-wrap items-center gap-3">
          <SegmentedControl v-model="language" :options="LANGUAGE_OPTIONS" label="Langue des avis" />
          <GameSearch field-id="recherche-mots" label="Un jeu" class="w-full sm:w-72" @select="selectGame" />
          <NuxtLink v-if="appid" :to="{ query: {} }" class="link">Tous les jeux</NuxtLink>
        </div>
      </template>
      <div v-if="words" class="grid gap-8 lg:grid-cols-2">
        <div v-for="side in sides" :key="side.title">
          <h3 class="mb-3 text-xl">{{ side.title }} <span class="text-base font-normal text-soft">· {{ formatNumber(side.reviews) }} avis</span></h3>
          <WordCloud v-if="side.words.length" :words="side.words" :color="side.color" :label="side.label" />
          <p v-else class="bg-deep p-6 text-soft">Aucun avis de ce côté.</p>
        </div>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption, ReviewWord, ReviewWords } from '~/types'
import type { GameOption } from '~/composables/useGameSearch'

type ReviewLanguage = 'english' | 'french'

const CLOUD_HEIGHT = 360
const LANGUAGE_OPTIONS: ChoiceOption<ReviewLanguage>[] = [
  { value: 'english', label: 'Anglais' },
  { value: 'french', label: 'Français' }
]

useHead({ title: 'Les mots des avis' })

const route = useRoute()
const appid = computed(() => Number(route.query.appid) || undefined)
const language = ref<ReviewLanguage>('english')

const { data: words, isLoading, hasError, refresh } = useApiResource<ReviewWords>(
  '/stats/review-words/',
  () => ({ language: language.value, appid: appid.value })
)

function selectGame(game: GameOption) {
  navigateTo({ query: { appid: game.appid } })
}

interface CloudSide {
  title: string
  reviews: number
  words: ReviewWord[]
  color: string
  label: string
}

const sides = computed<CloudSide[]>(() => {
  const current = words.value
  if (!current) return []
  const scope = current.name ?? 'tous les jeux'
  return [
    { title: '👍 Recommandé', ...current.positive, color: COLORS.hot, label: `Mots des avis positifs, ${scope}` },
    { title: '👎 Déconseillé', ...current.negative, color: SERIES_COLORS[2], label: `Mots des avis négatifs, ${scope}` }
  ]
})
</script>
