<template>
  <section>
    <h2 class="text-2xl leading-tight md:text-3xl">{{ title }}</h2>
    <p class="mb-4 mt-1 max-w-prose text-soft">{{ description }}</p>
    <ol class="space-y-px">
      <li v-for="game in games" :key="game.appid" class="flex items-center gap-3 bg-deep p-2">
        <GameCover
          :sources="wideCoverSources(game.appid, game.header_image)"
          :name="game.name"
          :width="92"
          :height="43"
          class="h-[43px] w-[92px] shrink-0"
        />
        <div class="min-w-0 flex-1">
          <NuxtLink :to="gameLink(game.appid)" class="font-semibold hover:text-hot">{{ game.name }}</NuxtLink>
          <p class="figure text-sm text-soft">
            {{ formatNumber(game.viewers) }} spectateurs, {{ formatNumber(game.players) }} joueurs
          </p>
        </div>
        <p class="figure shrink-0 text-xl font-semibold" :aria-label="`${game.hype_ratio} spectateur par joueur`">
          {{ formatRatio(game.hype_ratio) }}
        </p>
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
import type { HypeGame } from '~/types'

const RATIO_FORMAT = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 })

defineProps<{ title: string; description: string; games: HypeGame[] }>()

function formatRatio(ratio: number): string {
  return `×${RATIO_FORMAT.format(ratio)}`
}
</script>
