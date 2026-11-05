<template>
  <ul class="relative w-full" :style="{ aspectRatio }">
    <li
      v-for="(tile, index) in tiles"
      :key="tile.item.appid"
      class="wall-tile absolute border border-ground"
      :style="{
        left: `${tile.left}%`,
        top: `${tile.top}%`,
        width: `${tile.width}%`,
        height: `${tile.height}%`,
        animationDelay: `${index * TILE_STAGGER_MS}ms`
      }"
    >
      <NuxtLink :to="gameLink(tile.item.appid)" class="group absolute inset-0 block overflow-hidden focus-visible:z-10 focus-visible:-outline-offset-4">
        <GameCover
          :sources="sourcesOf(tile)"
          :name="tile.item.name"
          :width="COVER_WIDTH"
          :height="COVER_HEIGHT"
          :is-priority="index === 0"
          class="h-full w-full"
        />
        <GameChip :name="tile.item.name">
          <span class="figure">{{ formatNumber(tile.item.players) }}</span>
          <span class="sr-only"> joueurs</span>
        </GameChip>
      </NuxtLink>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { PlacedItem } from '~/utils/squarify'
import type { TopPlayedGame } from '~/types'

const TILE_STAGGER_MS = 40
const TALL_RATIO = 0.62
const PERCENT = 100
const COVER_WIDTH = 600
const COVER_HEIGHT = 900

const props = defineProps<{ games: TopPlayedGame[]; width: number; height: number }>()

const aspectRatio = computed(() => `${props.width} / ${props.height}`)
const ratio = computed(() => props.width / props.height)
const tiles = computed(() =>
  squarify(props.games.map((game) => ({ item: game, weight: game.players })), ratio.value)
)

/** Une tuile haute recadre fort l'image large (460 px) : elle prend la jaquette verticale. */
function sourcesOf(tile: PlacedItem<TopPlayedGame>): string[] {
  const realWidth = (tile.width / PERCENT) * ratio.value
  const realHeight = tile.height / PERCENT
  const { appid, header_image: headerImage } = tile.item
  return realHeight > realWidth * TALL_RATIO
    ? tallCoverSources(appid, headerImage)
    : wideCoverSources(appid, headerImage)
}
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .wall-tile {
    animation: tile-in 420ms ease-out both;
  }

  @keyframes tile-in {
    from {
      opacity: 0;
      transform: scale(0.97);
    }
  }
}
</style>
