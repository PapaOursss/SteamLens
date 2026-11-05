<template>
  <div>
    <PageIntro title="Les jeux que personne ne finit" is-lab>
      La part des joueurs qui débloquent chaque succès montre où ils lâchent ; le succès de fin d'histoire donne le taux de fin.
    </PageIntro>

    <DataBlock
      id="courbe"
      :title="details ? `Courbe d'abandon : ${details.name}` : 'Courbe d\'abandon'"
      note="Succès du plus courant au plus rare. En jaune, la fin de l'histoire."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!details?.curve.length"
      empty-message="Pas encore de succès importés pour ce jeu."
      :height="320"
      @retry="refresh()"
    >
      <template #actions>
        <GameSearch field-id="recherche-succes" label="Un autre jeu" class="w-full sm:w-80" @select="selectGame" />
      </template>
      <template v-if="details">
        <div class="mb-6 grid gap-x-8 gap-y-4 md:grid-cols-2">
          <StatTile label="Taux de fin" :value="details.completion_rate === null ? 'Non repéré' : formatPercent(details.completion_rate)" />
          <StatTile label="Plus gros décrochage" :value="details.biggest_drop ? `${formatNumber(details.biggest_drop.drop)} points` : '—'" :hint="dropHint" />
        </div>
        <AchievementCurveChart :curve="details.curve" :label="`Courbe d'abandon de ${details.name}`" />
      </template>
    </DataBlock>

    <DataBlock
      title="Les plus faibles taux de fin"
      note="Part des joueurs qui ont le succès de fin d'histoire. Source : Steam Web API."
      :is-loading="rankingLoading"
      :has-error="rankingError"
      :is-empty="!ranking?.length"
      empty-message="Pas encore de succès de fin repérés : l'import n'a pas tourné sur cette base."
      @retry="refreshRanking()"
    >
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Jeu</th>
              <th scope="col">Taux de fin</th>
              <th scope="col">Succès médian</th>
              <th scope="col">Succès</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in ranking" :key="game.appid">
              <td><NuxtLink :to="{ query: { appid: game.appid }, hash: '#courbe' }" class="link font-semibold">{{ game.name }}</NuxtLink></td>
              <td class="figure font-semibold">{{ formatPercent(game.completion_rate) }}</td>
              <td class="figure">{{ formatPercent(game.median_percent) }}</td>
              <td class="figure">{{ formatNumber(game.achievements) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { GameAchievements, LeastFinishedGame } from '~/types'

useHead({ title: 'Les jeux jamais finis' })

const { appid, selectGame } = useGameFromRoute()

const {
  data: ranking,
  isLoading: rankingLoading,
  hasError: rankingError,
  refresh: refreshRanking
} = useApiResource<LeastFinishedGame[]>('/stats/least-finished/')
const { data: details, isLoading, hasError, refresh } = useApiResource<GameAchievements>(() => `/stats/achievements/${appid.value}/`)

const dropHint = computed(() => {
  const drop = details.value?.biggest_drop
  return drop ? `Entre « ${drop.from_achievement} » et « ${drop.to_achievement} »` : undefined
})
</script>
