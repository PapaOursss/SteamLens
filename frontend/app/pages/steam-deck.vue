<template>
  <div class="deck-page">
    <header class="page-header">
      <h1 class="title">Compatibilité Linux & Steam Deck (ProtonDB)</h1>
      <p class="subtitle">
        Analyse de la jouabilité de la bibliothèque Steam sous Linux et Steam Deck grâce aux retours communautaires ProtonDB.
      </p>
    </header>

    <section class="section">
      <h2 class="section-title">Répartition globale des niveaux</h2>
      <div class="badges-showcase">
        <ProtonBadge tier="native" :total-reports="120" />
        <ProtonBadge tier="platinum" :score="0.95" :total-reports="450" />
        <ProtonBadge tier="gold" :score="0.82" :total-reports="320" />
        <ProtonBadge tier="silver" :score="0.65" :total-reports="180" />
        <ProtonBadge tier="bronze" :score="0.45" :total-reports="90" />
        <ProtonBadge tier="borked" :score="0.10" :total-reports="40" />
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Répartition par genre</h2>
      <div class="genre-table-wrapper">
        <table class="genre-table">
          <thead>
            <tr>
              <th>Genre</th>
              <th>Platinum</th>
              <th>Gold</th>
              <th>Silver</th>
              <th>Bronze</th>
              <th>Borked</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in genreBreakdown" :key="item.genre">
              <td class="font-bold">{{ item.genre }}</td>
              <td>{{ item.counts.platinum }}</td>
              <td>{{ item.counts.gold }}</td>
              <td>{{ item.counts.silver }}</td>
              <td>{{ item.counts.bronze }}</td>
              <td>{{ item.counts.borked }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ProtonBadge from '~/components/ProtonBadge.vue'

interface GenreProtonItem {
  genre: string
  counts: {
    platinum: number
    gold: number
    silver: number
    bronze: number
    borked: number
  }
}

const genreBreakdown = ref<GenreProtonItem[]>([
  { genre: 'Action', counts: { platinum: 142, gold: 89, silver: 34, bronze: 12, borked: 8 } },
  { genre: 'Indie', counts: { platinum: 310, gold: 45, silver: 12, bronze: 4, borked: 2 } },
  { genre: 'RPG', counts: { platinum: 98, gold: 64, silver: 28, bronze: 9, borked: 5 } },
  { genre: 'Strategy', counts: { platinum: 76, gold: 52, silver: 22, bronze: 15, borked: 6 } }
])
</script>

<style scoped>
.deck-page {
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
.badges-showcase { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; }
.genre-table-wrapper { overflow-x: auto; border: 1px solid #e5e7eb; border-radius: 0.5rem; }
.genre-table { width: 100%; border-collapse: collapse; text-align: left; }
.genre-table th, .genre-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; }
.genre-table th { background: #f9fafb; font-weight: 700; color: #374151; font-size: 0.85rem; }
.font-bold { font-weight: 600; }
</style>
