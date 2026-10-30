<template>
  <div class="playtime-page">
    <header class="page-header">
      <h1 class="title">Durée de vie des jeux & Rentabilité</h1>
      <p class="subtitle">
        Analyse du temps de jeu médian par genre et classement des jeux offrant le meilleur coût par heure de jeu.
      </p>
    </header>

    <section class="section">
      <h2 class="section-title">Temps de jeu médian par genre</h2>
      <div class="ridgeline-list">
        <div v-for="item in genreMedians" :key="item.genre" class="ridge-row">
          <div class="ridge-label">
            <span class="genre-name">{{ item.genre }}</span>
            <span class="median-val">{{ item.median_hours }} heures</span>
          </div>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ width: `${Math.min(100, (item.median_hours / maxHours) * 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Top 5 Rentabilité : Prix par heure jouée</h2>
      <div class="value-table-wrapper">
        <table class="value-table">
          <thead>
            <tr>
              <th>Jeu</th>
              <th>Temps médian</th>
              <th>Prix</th>
              <th>Coût / heure</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in bestValue" :key="game.appid">
              <td class="game-cell">
                <img :src="game.header_image" :alt="game.name" class="game-thumb" />
                <span class="game-name">{{ game.name }}</span>
              </td>
              <td>{{ game.median_hours }} h</td>
              <td>{{ game.price_eur > 0 ? `${game.price_eur.toFixed(2)} €` : 'Gratuit' }}</td>
              <td class="cost-cell">{{ game.cost_per_hour.toFixed(2) }} €/h</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface GenreMedianItem {
  genre: string
  median_hours: number
  sample_size: number
}

interface BestValueGame {
  appid: number
  name: string
  header_image: string
  median_hours: number
  price_eur: number
  cost_per_hour: number
}

const genreMedians = ref<GenreMedianItem[]>([
  { genre: 'RPG', median_hours: 48.5, sample_size: 150 },
  { genre: 'Strategy', median_hours: 36.0, sample_size: 110 },
  { genre: 'Simulation', median_hours: 24.5, sample_size: 85 },
  { genre: 'Action', median_hours: 14.0, sample_size: 220 },
  { genre: 'Indie', median_hours: 9.5, sample_size: 340 }
])

const bestValue = ref<BestValueGame[]>([
  {
    appid: 413150,
    name: 'Stardew Valley',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg',
    median_hours: 95.0,
    price_eur: 13.99,
    cost_per_hour: 0.15
  },
  {
    appid: 105600,
    name: 'Terraria',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/105600/header.jpg',
    median_hours: 80.0,
    price_eur: 9.99,
    cost_per_hour: 0.12
  },
  {
    appid: 289070,
    name: 'Sid Meier\'s Civilization VI',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/289070/header.jpg',
    median_hours: 120.0,
    price_eur: 29.99,
    cost_per_hour: 0.25
  }
])

const maxHours = computed(() => {
  return Math.max(...genreMedians.value.map(g => g.median_hours), 50)
})
</script>

<style scoped>
.playtime-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
}
.page-header { margin-bottom: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem; }
.title { font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.subtitle { color: #4b5563; margin: 0; }
.section { margin-bottom: 2.5rem; }
.section-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; }
.ridgeline-list { display: flex; flex-direction: column; gap: 0.75rem; }
.ridge-row { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 0.75rem 1rem; }
.ridge-label { display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-weight: 600; }
.median-val { color: #2563eb; }
.bar-track { height: 10px; background: #e5e7eb; border-radius: 9999px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); border-radius: 9999px; }
.value-table-wrapper { border: 1px solid #e5e7eb; border-radius: 0.5rem; overflow-x: auto; }
.value-table { width: 100%; border-collapse: collapse; text-align: left; }
.value-table th, .value-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; }
.value-table th { background: #f9fafb; font-size: 0.85rem; color: #374151; font-weight: 700; }
.game-cell { display: flex; align-items: center; gap: 0.75rem; }
.game-thumb { width: 50px; height: 25px; object-fit: cover; border-radius: 0.25rem; }
.game-name { font-weight: 600; }
.cost-cell { font-weight: 700; color: #16a34a; }
</style>
