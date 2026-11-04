<template>
  <div class="dashboard-page">
    <header class="dash-header">
      <div class="header-content">
        <h1 class="dash-title">SteamLens · Observatoire Steam en direct</h1>
        <p class="dash-subtitle">
          Données consolidées en temps réel : catalogue, affluence des joueurs et tendances économiques.
        </p>
      </div>
      <nav class="quick-nav">
        <NuxtLink to="/playtime" class="nav-btn">⏱️ Rentabilité</NuxtLink>
        <NuxtLink to="/hype" class="nav-btn">🔥 Twitch vs Steam</NuxtLink>
        <NuxtLink to="/minigame" class="nav-btn">🎮 Mini-jeu</NuxtLink>
        <NuxtLink to="/sources" class="nav-btn">📚 Méthodologie</NuxtLink>
      </nav>
    </header>

    <div v-if="pending" class="loading-state">
      <div class="spinner"></div>
      <p>Synchronisation avec le backend SteamLens...</p>
    </div>

    <div v-else-if="error" class="error-banner">
      Impossible de joindre l'API backend. Vérifiez que Django est actif.
    </div>

    <div v-else class="dash-body">
      <!-- 1. Tuiles chiffres clés -->
      <section class="tiles-grid">
        <MetricTile
          label="Jeux suivis"
          :value="formatNumber(stats.overview.games_count)"
          icon="🎮"
          hint="Catalogue consolidé"
        />
        <MetricTile
          label="Joueurs en direct"
          :value="formatNumber(stats.overview.total_players)"
          icon="👥"
          hint="Dernier snapshot cumulé"
        />
        <MetricTile
          label="Genre roi"
          :value="stats.overview.top_genre"
          icon="👑"
          hint="Plus grand volume de jeux"
        />
        <MetricTile
          label="Prix moyen"
          :value="`${stats.overview.average_price_eur.toFixed(2)} €`"
          icon="💶"
          hint="Converti au taux BCE"
        />
      </section>

      <!-- 2. Bandeau pépite du jour -->
      <FeaturedGem v-if="stats.featured_gem" :gem="stats.featured_gem" />

      <!-- 3. Top 10 des jeux les plus joués -->
      <section class="top-section">
        <h2 class="section-title">Top 10 des jeux les plus joués en ce moment</h2>
        <div class="top-list">
          <TopGameRow
            v-for="(game, index) in stats.top_games"
            :key="game.appid"
            :game="game"
            :rank="index + 1"
            :max-players="maxPlayers"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FeaturedGem from '~/components/FeaturedGem.vue'
import MetricTile from '~/components/MetricTile.vue'
import TopGameRow from '~/components/TopGameRow.vue'
import type { DashboardData } from '~/types/dashboard'

const fallbackData: DashboardData = {
  overview: {
    games_count: 50400,
    total_players: 18452000,
    top_genre: 'Action',
    average_price_eur: 14.99,
  },
  featured_gem: {
    appid: 413150,
    name: 'Stardew Valley',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg',
    short_description: 'Vous venez d\'hériter de la vieille parcelle agricole de votre grand-père...',
    price_eur: 13.99,
  },
  top_games: [
    {
      appid: 730,
      name: 'Counter-Strike 2',
      header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg',
      players: 1250000,
      sparkline: [950000, 1020000, 1100000, 1250000, 1180000, 1250000],
    },
    {
      appid: 570,
      name: 'Dota 2',
      header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/570/header.jpg',
      players: 640000,
      sparkline: [510000, 540000, 600000, 640000, 620000, 640000],
    },
    {
      appid: 578080,
      name: 'PUBG: BATTLEGROUNDS',
      header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/578080/header.jpg',
      players: 480000,
      sparkline: [380000, 420000, 450000, 470000, 460000, 480000],
    },
  ],
}

const { data, pending, error } = await useFetch<DashboardData>('http://localhost:8000/api/stats/dashboard/', {
  lazy: true,
  default: () => fallbackData,
})

const stats = computed<DashboardData>(() => data.value || fallbackData)

const maxPlayers = computed(() => {
  const list = stats.value.top_games
  return list.length > 0 ? Math.max(...list.map((g) => g.players)) : 1
})

function formatNumber(num: number): string {
  return (num || 0).toLocaleString('fr-FR')
}
</script>

<style scoped>
.dashboard-page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1f2937;
}
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.dash-title {
  font-size: 2.1rem;
  font-weight: 800;
  margin: 0 0 0.4rem 0;
  color: #111827;
}
.dash-subtitle {
  color: #4b5563;
  margin: 0;
  font-size: 1rem;
}
.quick-nav {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.nav-btn {
  background: #f3f4f6;
  color: #374151;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.5rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.15s ease;
}
.nav-btn:hover {
  background: #e5e7eb;
  color: #111827;
}
.tiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}
.top-section {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 1.25rem 0;
  color: #111827;
}
.top-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.loading-state, .error-banner {
  padding: 3rem;
  text-align: center;
  border-radius: 0.5rem;
}
.loading-state { color: #6b7280; }
.error-banner { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
