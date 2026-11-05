<template>
  <section class="gutter grid gap-4 pb-6 pt-8 md:pt-12 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-end lg:gap-10">
    <h1 class="text-4xl leading-none sm:text-5xl lg:text-7xl">
      La surface de chaque jeu, c'est son nombre de joueurs.
    </h1>
    <p class="max-w-prose text-lg leading-relaxed text-soft">
      <template v-if="overview">
        <strong class="font-semibold text-text">{{ formatNumber(overview.total_players) }} joueurs</strong>
        sur les {{ formatNumber(overview.games_count) }} jeux suivis.
      </template>
      <template v-if="takenAt"> Steam Web API, relevé du {{ formatDateTime(takenAt) }}.</template>
    </p>
  </section>
</template>

<script setup lang="ts">
import type { DashboardOverview } from '~/types'

defineProps<{ overview?: DashboardOverview; takenAt?: string }>()
</script>
