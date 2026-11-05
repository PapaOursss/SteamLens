<template>
  <div class="sales-page">
    <header class="page-header">
      <h1 class="title">Ventes par Région (Kaggle vgsales)</h1>
      <p class="subtitle">
        Comparaison des préférences culturelles et genres préférés : Amérique du Nord, Europe, Japon et Reste du Monde.
      </p>
    </header>

    <!-- Mini-carte interactive du monde -->
    <section class="section">
      <div class="section-heading">
        <h2 class="section-title">Carte interactive des ventes mondiales</h2>
        <span class="section-badge">Interactif</span>
      </div>
      <RegionalSalesMap />
    </section>

    <!-- Bannière synthétique des préférences -->
    <section class="section">
      <h2 class="section-title">Synthèse des spécificités culturelles</h2>
      <div class="favorites-banner">
        <div class="fav-card">
          <span class="region-flag">🇺🇸 / 🇨🇦 Amérique du Nord</span>
          <strong class="fav-genre">Action & Tir (Shooter)</strong>
          <span class="fav-desc">Marché orienté blockbusters AAA et multijoueur compétitif.</span>
        </div>
        <div class="fav-card">
          <span class="region-flag">🇪🇺 Europe</span>
          <strong class="fav-genre">Action & Sports</strong>
          <span class="fav-desc">Domination marquée des simulations de football et sports mécaniques.</span>
        </div>
        <div class="fav-card fav-highlight">
          <span class="region-flag">🇯🇵 Japon</span>
          <strong class="fav-genre">Jeux de Rôle (J-RPG)</strong>
          <span class="fav-desc">Unique au monde : le RPG dépasse tous les autres genres combinés.</span>
        </div>
        <div class="fav-card">
          <span class="region-flag">🌐 Reste du Monde</span>
          <strong class="fav-genre">Action & Sports</strong>
          <span class="fav-desc">Forte diffusion des franchises universelles (GTA, FIFA).</span>
        </div>
      </div>
    </section>

    <!-- Tableau détaillé par genre -->
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
              <th>Total Mondial</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in salesData" :key="item.genre">
              <td class="font-bold">{{ item.genre }}</td>
              <td>{{ item.na }} M</td>
              <td>{{ item.eu }} M</td>
              <td :class="item.genre === 'Role-Playing' ? 'jp-special' : ''">{{ item.jp }} M</td>
              <td class="font-bold">{{ (item.na + item.eu + item.jp).toFixed(1) }} M</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RegionalSalesMap from '~/components/RegionalSalesMap.vue'

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
  { genre: 'Misc', na: 402.5, eu: 213.8, jp: 107.8 },
  { genre: 'Racing', na: 359.4, eu: 238.4, jp: 56.7 }
])
</script>

<style scoped>
.sales-page {
  max-width: 1040px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
}

.page-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
  color: #0f172a;
}

.subtitle {
  color: #64748b;
  margin: 0;
}

.section {
  margin-bottom: 3rem;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.section-badge {
  background: #e0e7ff;
  color: #4338ca;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.favorites-banner {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.fav-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.fav-highlight {
  background: #fff1f2;
  border-color: #fecdd3;
}

.region-flag {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

.fav-genre {
  font-size: 1.15rem;
  color: #0f172a;
}

.fav-desc {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
}

.table-container {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sales-table th,
.sales-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.sales-table th {
  background: #f8fafc;
  font-weight: 700;
  font-size: 0.85rem;
  color: #334155;
}

.font-bold {
  font-weight: 600;
}

.jp-special {
  color: #e11d48;
  font-weight: 700;
}
</style>
