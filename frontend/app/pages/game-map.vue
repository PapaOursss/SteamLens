<template>
  <div>
    <PageIntro title="La carte des jeux" is-lab>
      Chaque point est un jeu, placé selon ses tags : deux jeux proches sur la carte se ressemblent. La couleur donne le tag principal, la taille le nombre de propriétaires.
    </PageIntro>

    <DataBlock
      title="Le catalogue en un nuage"
      note="Les jeux les plus possédés, projetés en 2D par t-SNE à partir de leurs tags pondérés (SteamSpy). Les axes n'ont pas d'unité : seules les distances comptent. Cliquer un point ouvre sa fiche."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!map?.points.length"
      empty-message="La carte n'est pas encore calculée : lancer manage.py compute_similar_games."
      :height="MAP_HEIGHT"
      @retry="refresh()"
    >
      <template #actions>
        <GameSearch field-id="recherche-carte" label="Situer un jeu" class="w-full sm:w-80" @select="locateGame" />
      </template>
      <p v-if="selectedAppid && !isPlaced" class="mb-3 text-soft">Ce jeu n'est pas sur la carte : elle ne garde que les jeux les plus possédés.</p>
      <GameMapChart
        v-if="map"
        :points="map.points"
        :families="map.families"
        :selected-appid="selectedAppid"
        :height="MAP_HEIGHT"
        label="Nuage de points des jeux placés selon leurs tags"
        @select="openGame"
      />
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { GameMap, GameMapPoint } from '~/types'
import type { GameOption } from '~/composables/useGameSearch'

const MAP_HEIGHT = 620

useHead({ title: 'La carte des jeux' })

const route = useRoute()
const selectedAppid = computed(() => Number(route.query.appid) || undefined)

const { data: map, isLoading, hasError, refresh } = useApiResource<GameMap>('/stats/game-map/')

const isPlaced = computed(() => map.value?.points.some((point) => point.appid === selectedAppid.value) ?? false)

function locateGame(game: GameOption) {
  navigateTo({ query: { appid: game.appid } })
}

function openGame(point: GameMapPoint) {
  navigateTo(gameLink(point.appid))
}
</script>
