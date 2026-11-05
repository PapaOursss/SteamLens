<template>
  <div>
    <PageIntro title="Combien de temps, pour quel prix" is-lab>
      Le temps qu'on passe vraiment sur chaque genre, et les jeux dont l'heure revient le moins cher.
    </PageIntro>

    <DataBlock
      title="Temps de jeu médian par genre"
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!genreRows.length"
      empty-message="Pas encore de données : l'import du temps de jeu n'a pas tourné sur cette base."
      @retry="refresh()"
    >
      <div class="max-w-3xl"><RankBars :rows="genreRows" /></div>
    </DataBlock>

    <DataBlock
      title="L'heure de jeu la moins chère"
      note="Prix du dernier relevé divisé par le temps de jeu médian."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.best_value.length"
      empty-message="Pas encore de données : il faut des temps de jeu et des prix relevés."
      @retry="refresh()"
    >
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Jeu</th>
              <th scope="col">Temps médian</th>
              <th scope="col">Prix</th>
              <th scope="col">Coût de l'heure</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in data?.best_value" :key="game.appid">
              <td><NuxtLink :to="gameLink(game.appid)" class="link font-semibold">{{ game.name }}</NuxtLink></td>
              <td class="figure">{{ formatHours(game.median_hours) }}</td>
              <td class="figure">{{ formatPrice(game.price_eur) }}</td>
              <td class="figure font-semibold">{{ formatPrice(game.cost_per_hour) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { PlaytimeStats, RankRow } from '~/types'

useHead({ title: 'Durée de vie' })

const { data, isLoading, hasError, refresh } = useApiResource<PlaytimeStats>('/stats/playtime/')

function formatHours(hours: number): string {
  return `${formatNumber(hours)} h`
}

const genreRows = computed<RankRow[]>(() =>
  (data.value?.by_genre ?? [])
    .filter((item) => item.median_hours > 0)
    .sort((first, second) => second.median_hours - first.median_hours)
    .map((item) => ({
      key: item.genre,
      label: item.genre,
      value: item.median_hours,
      display: formatHours(item.median_hours)
    }))
)
</script>
