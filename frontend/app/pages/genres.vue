<template>
  <div class="genres-page">
    <header class="page-header">
      <h1 class="title">Genres et Tags : Treemap & Sunburst</h1>
      <p class="subtitle">
        Visualisation hiérarchique des genres Steam et de la classification IGDB.
      </p>
    </header>

    <!-- Contrôles du Treemap -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2 class="section-title">Treemap Genres & Tags Steam</h2>
          <p class="section-desc">
            La couleur indique la note moyenne Metacritic (vert = excellent, rouge = faible, gris = non noté).
          </p>
        </div>
        <div class="mode-toggle">
          <button
            class="toggle-btn"
            :class="{ active: mode === 'games' }"
            @click="mode = 'games'"
          >
            Nombre de jeux
          </button>
          <button
            class="toggle-btn"
            :class="{ active: mode === 'players' }"
            @click="mode = 'players'"
          >
            Nombre de joueurs
          </button>
        </div>
      </div>

      <div class="legend-bar">
        <span class="legend-label">Note Metacritic :</span>
        <div class="legend-items">
          <span class="legend-color score-80">≥ 80 (Excellent)</span>
          <span class="legend-color score-70">70 - 79 (Très bon)</span>
          <span class="legend-color score-60">60 - 69 (Moyen)</span>
          <span class="legend-color score-50">&lt; 60 (Passable)</span>
          <span class="legend-color score-none">Non noté</span>
        </div>
      </div>

      <TreemapChart :data="treemapData" :mode="mode" />
    </section>

    <!-- Sunburst IGDB -->
    <section class="section">
      <h2 class="section-title">Sunburst IGDB : Genre → Thème → Mode</h2>
      <p class="section-desc">
        Explorez la taxonomie détaillée d'IGDB à trois niveaux : cliquez sur un genre ou thème pour explorer ses ramifications.
      </p>

      <SunburstChart :data="sunburstData" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TreemapChart, { type TreemapGenreNode } from '~/components/TreemapChart.vue'
import SunburstChart, { type SunburstGenre } from '~/components/SunburstChart.vue'

const mode = ref<'games' | 'players'>('games')

const treemapData = ref<TreemapGenreNode[]>([
  {
    id: 'genre-1',
    name: 'Action',
    games: 450,
    owners: 120000000,
    score: 78.5,
    children: [
      { id: 'tag-1-1', name: 'FPS', games: 180, owners: 85000000, score: 82.0, votes: 12000 },
      { id: 'tag-1-2', name: 'Open World', games: 110, owners: 22000000, score: 79.0, votes: 8500 },
      { id: 'tag-1-3', name: 'Fast-Paced', games: 95, owners: 8000000, score: 75.0, votes: 4100 },
      { id: 'tag-1-4', name: 'Shooter', games: 65, owners: 5000000, score: 72.0, votes: 3200 }
    ]
  },
  {
    id: 'genre-2',
    name: 'Indie',
    games: 1200,
    owners: 35000000,
    score: 80.2,
    children: [
      { id: 'tag-2-1', name: 'Roguelike', games: 320, owners: 15000000, score: 84.0, votes: 16000 },
      { id: 'tag-2-2', name: 'Pixel Graphics', games: 410, owners: 9000000, score: 79.5, votes: 11000 },
      { id: 'tag-2-3', name: '2D', games: 310, owners: 7000000, score: 78.0, votes: 8900 },
      { id: 'tag-2-4', name: 'Story Rich', games: 160, owners: 4000000, score: 81.0, votes: 5400 }
    ]
  },
  {
    id: 'genre-3',
    name: 'RPG',
    games: 310,
    owners: 65000000,
    score: 83.4,
    children: [
      { id: 'tag-3-1', name: 'Action RPG', games: 140, owners: 38000000, score: 85.0, votes: 14000 },
      { id: 'tag-3-2', name: 'Turn-Based', games: 90, owners: 15000000, score: 81.5, votes: 7800 },
      { id: 'tag-3-3', name: 'JRPG', games: 80, owners: 12000000, score: 82.0, votes: 6200 }
    ]
  },
  {
    id: 'genre-4',
    name: 'Strategy',
    games: 280,
    owners: 28000000,
    score: 77.0,
    children: [
      { id: 'tag-4-1', name: 'City Builder', games: 110, owners: 12000000, score: 79.0, votes: 8000 },
      { id: 'tag-4-2', name: 'Turn-Based Strategy', games: 95, owners: 10000000, score: 76.5, votes: 5600 },
      { id: 'tag-4-3', name: 'RTS', games: 75, owners: 6000000, score: 74.0, votes: 4200 }
    ]
  }
])

const sunburstData = ref<SunburstGenre[]>([
  {
    name: 'Role-playing (RPG)',
    value: 380,
    children: [
      {
        name: 'Fantasy',
        value: 220,
        children: [
          { name: 'Single player', value: 160 },
          { name: 'Co-operative', value: 60 }
        ]
      },
      {
        name: 'Science fiction',
        value: 110,
        children: [
          { name: 'Single player', value: 85 },
          { name: 'Multiplayer', value: 25 }
        ]
      }
    ]
  },
  {
    name: 'Shooter',
    value: 290,
    children: [
      {
        name: 'Warfare',
        value: 150,
        children: [
          { name: 'Multiplayer', value: 120 },
          { name: 'Single player', value: 30 }
        ]
      }
    ]
  }
])
</script>

<style scoped>
.genres-page {
  max-width: 1080px;
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
}

.subtitle {
  color: #4b5563;
  margin: 0;
}

.section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 0.35rem 0;
}

.section-desc {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.mode-toggle {
  display: flex;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.toggle-btn {
  padding: 0.4rem 0.85rem;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
  border-radius: 0.35rem;
  cursor: pointer;
}

.toggle-btn.active {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.legend-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.8rem;
  color: #4b5563;
}

.legend-items {
  display: flex;
  gap: 0.35rem;
}

.legend-color {
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  color: white;
  font-weight: 600;
}

.score-80 { background: #059669; }
.score-70 { background: #0284c7; }
.score-60 { background: #d97706; }
.score-50 { background: #ea580c; }
.score-none { background: #475569; }
</style>
