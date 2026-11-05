<template>
  <div>
    <PageIntro title="Plus ou moins" is-lab>
      <p v-if="round">Le chiffre de ce duel : <strong class="font-semibold text-text">{{ METRICS[round.metric].label }}</strong>.</p>
      <p class="figure mt-1">Bonnes réponses : {{ score }}. Meilleure série : {{ bestStreak }}.</p>
    </PageIntro>

    <div v-if="isDrawing" class="aspect-[2/1] animate-pulse bg-deep motion-reduce:animate-none" />
    <div v-else-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Le duel n'arrive pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="nextRound()">Réessayer</button>
    </div>
    <div v-else-if="round" class="grid gap-px md:grid-cols-2">
      <article class="bg-deep">
        <GameCover :sources="wideCoverSources(round.game_a.appid, round.game_a.header_image)" :name="round.game_a.name" :width="460" :height="215" is-priority class="aspect-[460/215] w-full" />
        <div class="p-4 md:p-6">
          <h2 class="text-2xl leading-tight md:text-3xl">{{ round.game_a.name }}</h2>
          <p class="figure mt-2 font-display text-4xl font-extrabold">{{ valueOf(round.game_a) }}</p>
        </div>
      </article>

      <article class="bg-deep">
        <GameCover :sources="wideCoverSources(round.game_b.appid, round.game_b.header_image)" :name="round.game_b.name" :width="460" :height="215" is-priority class="aspect-[460/215] w-full" />
        <div class="p-4 md:p-6">
          <h2 class="text-2xl leading-tight md:text-3xl">{{ round.game_b.name }}</h2>
          <p v-if="!guess" class="mt-2 text-lg text-soft">Plus ou moins que {{ valueOf(round.game_a) }} ?</p>
          <div v-if="!guess" class="mt-3 flex flex-wrap gap-2">
            <button type="button" class="button text-lg" @click="answer('higher')">Plus</button>
            <button type="button" class="button text-lg" @click="answer('lower')">Moins</button>
          </div>
          <div v-else aria-live="polite">
            <p class="figure mt-2 font-display text-4xl font-extrabold">{{ valueOf(round.game_b) }}</p>
            <p class="mt-1 text-lg">{{ verdict }}</p>
            <button type="button" class="button mt-3" @click="nextRound()">Duel suivant</button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DuelGame, DuelMetric, DuelRound } from '~/types'

type Guess = 'higher' | 'lower'

const METRICS: Record<DuelMetric, { label: string; format: (value: number) => string }> = {
  players: { label: 'joueurs connectés', format: (value) => `${formatNumber(value)} joueurs` },
  price_eur: { label: 'prix en euros', format: (value) => (value > 0 ? formatPrice(value) : 'Gratuit') },
  review_score: { label: "part d'avis positifs", format: (value) => `${value} %` }
}

useHead({ title: 'Plus ou moins' })

const { data: round, isLoading, hasError, refresh } = useApiResource<DuelRound>('/minigame/duel/')

/** Prix 0 = jeu gratuit ; joueurs ou avis à 0 = pas de relevé, donc rien à deviner. */
const ZERO_MEANS_MISSING: DuelMetric[] = ['players', 'review_score']
const MAX_REDRAWS = 5

const redraws = ref(0)

function isComparable({ game_a: first, game_b: second, metric }: DuelRound): boolean {
  return !ZERO_MEANS_MISSING.includes(metric) || (first[metric] > 0 && second[metric] > 0)
}

watch(round, (drawn) => {
  if (drawn && !isComparable(drawn) && redraws.value < MAX_REDRAWS) {
    redraws.value++
    refresh()
  } else {
    redraws.value = 0
  }
})

const isDrawing = computed(() => isLoading.value || (round.value ? !isComparable(round.value) && redraws.value > 0 : false))

const guess = ref<Guess | null>(null)
const score = ref(0)
const streak = ref(0)
const bestStreak = ref(0)
const isRight = ref(false)

function metricOf(game: DuelGame): number {
  return game[round.value!.metric]
}

function valueOf(game: DuelGame): string {
  return METRICS[round.value!.metric].format(metricOf(game))
}

const isTie = computed(() => round.value !== null && round.value !== undefined && metricOf(round.value.game_a) === metricOf(round.value.game_b))
const verdict = computed(() => {
  if (isTie.value) return 'Égalité : le point est pour vous.'
  return isRight.value ? 'Bien vu.' : 'Raté.'
})

function answer(choice: Guess) {
  const first = metricOf(round.value!.game_a)
  const second = metricOf(round.value!.game_b)
  isRight.value = choice === 'higher' ? second >= first : second <= first
  guess.value = choice
  streak.value = isRight.value ? streak.value + 1 : 0
  if (isRight.value) score.value++
  bestStreak.value = Math.max(bestStreak.value, streak.value)
}

function nextRound() {
  guess.value = null
  refresh()
}
</script>
