<template>
  <div>
    <PageIntro title="Avis et review bombings" is-lab>
      Le ratio d'avis positifs par langue et semaine par semaine, et ses chutes brutales. Seuls des comptes sont gardés : ni auteur ni SteamID.
    </PageIntro>

    <DataBlock
      id="jeu"
      :title="reviews?.name ?? 'Un jeu'"
      note="Source : boutique Steam. En jaune, les semaines de review bombing."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!reviews?.weeks.length && !reviews?.languages.length"
      empty-message="Pas encore d'avis importés pour ce jeu."
      :height="300"
      @retry="refresh()"
    >
      <template #actions>
        <GameSearch field-id="recherche-avis" label="Un autre jeu" class="w-full sm:w-80" @select="selectGame" />
      </template>
      <div v-if="reviews" class="grid gap-8 xl:grid-cols-2">
        <div v-if="reviews.weeks.length">
          <h3 class="mb-3 text-xl">Par semaine</h3>
          <ReviewWeeksChart :weeks="reviews.weeks" :bombings="reviews.bombings" :label="`Ratio d'avis positifs de ${reviews.name} par semaine`" />
        </div>
        <div v-if="languageRows.length">
          <h3 class="mb-3 text-xl">Par langue</h3>
          <RankBars :rows="languageRows" :maximum="PERCENT" />
        </div>
      </div>
    </DataBlock>

    <DataBlock
      title="Review bombings repérés"
      note="Semaines où le ratio positif chute d'au moins 20 points sous les 4 précédentes."
      :is-loading="bombingsLoading"
      :has-error="bombingsError"
      :is-empty="!bombings?.length"
      empty-message="Aucune chute brutale repérée, ou l'import des avis n'a pas tourné sur cette base."
      @retry="refreshBombings()"
    >
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Jeu</th>
              <th scope="col">Semaine du</th>
              <th scope="col">Avant</th>
              <th scope="col">Pendant</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in bombings" :key="`${row.appid}-${row.week_start}`">
              <td><NuxtLink :to="{ query: { appid: row.appid }, hash: '#jeu' }" class="link font-semibold">{{ row.name }}</NuxtLink></td>
              <td class="figure">{{ formatDate(row.week_start) }}</td>
              <td class="figure">{{ shareLabel(row.baseline_share) }}</td>
              <td class="figure font-semibold">{{ shareLabel(row.positive_share) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { BombedGame, GameReviews, RankRow } from '~/types'

const PERCENT = 100

useHead({ title: 'Avis et review bombings' })

const { appid, selectGame } = useGameFromRoute()

const {
  data: bombings,
  isLoading: bombingsLoading,
  hasError: bombingsError,
  refresh: refreshBombings
} = useApiResource<BombedGame[]>('/stats/review-bombings/')
const { data: reviews, isLoading, hasError, refresh } = useApiResource<GameReviews>(() => `/stats/reviews/${appid.value}/`)

function shareLabel(share: number): string {
  return formatPercent(Math.round(share * PERCENT))
}

const languageRows = computed<RankRow[]>(() =>
  [...(reviews.value?.languages ?? [])]
    .sort((first, second) => second.positive_share - first.positive_share)
    .map((row) => ({
      key: row.language,
      label: row.language,
      value: row.positive_share * PERCENT,
      display: shareLabel(row.positive_share)
    }))
)
</script>
