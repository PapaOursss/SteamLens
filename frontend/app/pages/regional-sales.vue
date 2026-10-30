<template>
  <div class="sales-page">
    <header class="page-header">
      <h1 class="title">Ventes par Région (Kaggle vgsales)</h1>
      <p class="subtitle">
        Comparaison des préférences culturelles et genres préférés : Amérique du Nord, Europe et Japon.
      </p>
    </header>

    <section class="section favorites-banner">
      <div class="fav-card">
        <span class="region-flag">🇺🇸 / 🇨🇦 Amérique du Nord</span>
        <strong class="fav-genre">Action & Tir</strong>
      </div>
      <div class="fav-card">
        <span class="region-flag">🇪🇺 Europe</span>
        <strong class="fav-genre">Action & Sports</strong>
      </div>
      <div class="fav-card fav-highlight">
        <span class="region-flag">🇯🇵 Japon</span>
        <strong class="fav-genre">Jeux de Rôle (J-RPG)</strong>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Volumes de ventes par genre (Millions d'unités)</h2>
      <div class="table-container">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Genre</th>
              <th>Amérique du Nord</th>
              <th>Europe</th>
              <th>Japon</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in salesData" :key="item.genre">
              <td class="font-bold">{{ item.genre }}</td>
              <td>{{ item.na }} M</td>
              <td>{{ item.eu }} M</td>
              <td :class="item.genre === 'Role-Playing' ? 'jp-special' : ''">{{ item.jp }} M</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface RegionalGenreSales {
  genre: string
  na: number
  eu: number
  jp: number
}

const salesData = ref<RegionalGenreSales[]>([
  { genre: 'Action', na: 877.8, eu: 525.0, jp: 159.9 },
  { genre: 'Sports', na: 683.3, eu: 376.5, jp: 135.4 },
  { genre: 'Shooter', na: 582.6, eu: 313.2, jp: 38.3 },
  { genre: 'Role-Playing', na: 319.5, eu: 183.6, jp: 344.9 },
  { genre: 'Platform', na: 447.0, eu: 201.6, jp: 130.8 },
  { genre: 'Misc', na: 402.5, eu: 213.8, jp: 107.8 }
])
</script>

<style scoped>
.sales-page {
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
.favorites-banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}
.fav-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.fav-highlight {
  background: #fdf2f8;
  border-color: #fbcfe8;
}
.region-flag { font-size: 0.85rem; color: #6b7280; font-weight: 600; }
.fav-genre { font-size: 1.15rem; color: #111827; }
.table-container { border: 1px solid #e5e7eb; border-radius: 0.5rem; overflow-x: auto; }
.sales-table { width: 100%; border-collapse: collapse; text-align: left; }
.sales-table th, .sales-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; }
.sales-table th { background: #f9fafb; font-weight: 700; font-size: 0.85rem; color: #374151; }
.font-bold { font-weight: 600; }
.jp-special { color: #db2777; font-weight: 700; }
</style>
