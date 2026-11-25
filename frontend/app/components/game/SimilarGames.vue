<template>
  <DataBlock
    title="Si tu aimes ce jeu…"
    note="Les jeux dont les tags votés par les joueurs ressemblent le plus à ceux-ci (similarité cosinus des tags SteamSpy)."
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!games?.length"
    empty-message="Pas encore de jeux similaires calculés pour ce jeu."
    @retry="refresh()"
  >
    <template #actions>
      <NuxtLink :to="`/game-map?appid=${appid}`" class="link">Voir sur la carte des jeux</NuxtLink>
    </template>
    <ul class="grid gap-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <li v-for="game in games" :key="game.appid">
        <GameTile :appid="game.appid" :name="game.name" :header-image="game.header_image">
          {{ Math.round(game.score * PERCENT) }} % proches<template v-if="game.shared_tags.length"> · {{ game.shared_tags.join(', ') }}</template>
        </GameTile>
      </li>
    </ul>
  </DataBlock>
</template>

<script setup lang="ts">
import type { SimilarGame } from '~/types'

const PERCENT = 100

const props = defineProps<{ appid: number }>()

const { data: games, isLoading, hasError, refresh } = useApiResource<SimilarGame[]>(() => `/games/${props.appid}/similar/`)
</script>
