<template>
  <div>
    <PageIntro title="Comparer des jeux" is-lab>
      <template #under-title>
        <GameSearch v-if="ids.length < MAX_COMPARED" field-id="recherche-comparer" label="Ajouter un jeu" class="mt-5 max-w-md" @select="add($event.appid)" />
      </template>
      De deux à quatre jeux. L'adresse de la page garde votre choix : copiez-la pour le partager.
    </PageIntro>

    <ul v-if="games.length" class="gutter grid grid-cols-2 gap-4 lg:grid-cols-4">
      <li v-for="{ game } in games" :key="game.appid">
        <GameTile :appid="game.appid" :name="game.name" :header-image="game.header_image" />
        <button type="button" class="button-quiet mt-2 w-full" :aria-label="`Retirer ${game.name}`" @click="remove(game.appid)">Retirer</button>
      </li>
    </ul>

    <p v-if="missing.length" class="gutter py-4" role="alert">
      Introuvables, ou l'API ne répond pas : {{ missing.join(', ') }}.
      <button type="button" class="link" @click="reload()">Réessayer</button>
    </p>

    <p v-if="!isLoading && games.length < MINIMUM_COMPARED" class="gutter py-8 text-soft">
      Choisissez au moins deux jeux, par exemple
      <NuxtLink to="/comparer?ids=730,570" class="link">Counter-Strike 2 et Dota 2</NuxtLink>.
    </p>

    <template v-if="games.length >= MINIMUM_COMPARED">
      <DataBlock title="ADN superposés" note="Rang de 0 à 100 parmi les jeux suivis. Une mesure absente est dessinée à 0." :is-empty="!axes.length" empty-message="Pas assez de données.">
        <ComparedRadar :axes="axes" :series="radarSeries" :height="440" label="Radars superposés des jeux comparés" />
      </DataBlock>
      <DataBlock title="Joueurs connectés" note="Moyenne par mois." :is-empty="!hasPlayers" empty-message="Aucun relevé de joueurs.">
        <ComparedLines :series="playerSeries" :height="380" label="Joueurs des jeux comparés" :format-value="formatCompact" />
      </DataBlock>
      <DataBlock title="Prix en France" note="Source : IsThereAnyDeal." :is-empty="!hasPrices" empty-message="Pas encore d'historique de prix pour ces jeux.">
        <ComparedLines :series="priceSeries" :height="380" is-step label="Prix des jeux comparés" :format-value="formatPrice" />
      </DataBlock>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { GameDnaKey } from '~/types'

const MINIMUM_COMPARED = 2
const AXIS_LABELS: Record<GameDnaKey, string> = {
  rating: 'Note',
  popularity: 'Popularité',
  price: 'Prix',
  lifespan: 'Durée de vie',
  twitch: 'Buzz Twitch',
  achievement_rarity: 'Rareté des succès'
}
const AXIS_KEYS = Object.keys(AXIS_LABELS) as GameDnaKey[]

useHead({ title: 'Comparer des jeux' })

const { ids, games, missing, isLoading, add, remove, reload } = useComparedGames()

const axes = computed(() =>
  games.value.some(({ dna }) => dna.some(({ score }) => score !== null)) ? Object.values(AXIS_LABELS) : []
)
const radarSeries = computed(() =>
  games.value.map(({ game, dna }) => ({
    name: game.name,
    scores: AXIS_KEYS.map((key) => dna.find((axis) => axis.key === key)?.score ?? null)
  }))
)
const playerSeries = computed(() =>
  games.value.map(({ game, players }) => ({ name: game.name, points: monthlyPlayers(players) }))
)
const priceSeries = computed(() =>
  games.value.map(({ game, prices }) => ({
    name: game.name,
    points: (prices?.changes ?? []).map((change) => ({ date: change.changed_at, value: change.price }))
  }))
)
const hasPlayers = computed(() => playerSeries.value.some(({ points }) => points.length))
const hasPrices = computed(() => priceSeries.value.some(({ points }) => points.length))
</script>
