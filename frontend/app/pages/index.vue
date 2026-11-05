<template>
  <div>
    <GameWall v-if="topGames.length" :games="topGames" />
    <div v-else-if="isLoadingTop" class="aspect-[375/640] animate-pulse bg-deep motion-reduce:animate-none md:aspect-[1440/700]" />
    <div v-else class="gutter flex flex-wrap items-center gap-4 bg-deep py-10" role="alert">
      <p>{{ hasTopError ? "Le classement n'arrive pas : l'API de SteamLens ne répond pas." : 'Pas encore de relevé de joueurs.' }}</p>
      <button v-if="hasTopError" type="button" class="button" @click="refreshTop()">Réessayer</button>
    </div>

    <HomeIntro :overview="dashboard?.overview" :taken-at="topGames[0]?.taken_at" />
    <GamePlayersHistory v-if="topGames[0]" :appid="topGames[0].appid" :name="topGames[0].name" />
    <HomePrices />
    <HomeGem v-if="dashboard?.featured_gem" :gem="dashboard.featured_gem" />
  </div>
</template>

<script setup lang="ts">
import type { DashboardData, TopPlayedGame } from '~/types'

const {
  data: top,
  isLoading: isLoadingTop,
  hasError: hasTopError,
  refresh: refreshTop
} = useApiResource<TopPlayedGame[]>('/stats/top-played/')
const { data: dashboard } = useApiResource<DashboardData>('/stats/dashboard/')

const topGames = computed(() => top.value ?? [])
</script>
