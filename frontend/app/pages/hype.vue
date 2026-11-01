<template>
  <div class="hype-page">
    <header class="page-header">
      <h1 class="title">Hype contre Réalité : Twitch vs Steam</h1>
      <p class="subtitle">
        Comparaison entre l'audience Twitch (spectateurs) et la fréquentation réelle Steam (joueurs en jeu).
      </p>
    </header>

    <div class="extremes-grid">
      <section class="section extreme-card">
        <h2 class="section-title title-watched">Regardés plus que joués (Hype forte)</h2>
        <p class="section-desc">Ces jeux attirent proportionnellement beaucoup plus de spectateurs que de joueurs actifs.</p>
        <div class="game-list">
          <div v-for="game in watchedMore" :key="game.appid" class="game-item">
            <img :src="game.header_image" :alt="game.name" class="game-cover" />
            <div class="game-info">
              <span class="game-name">{{ game.name }}</span>
              <div class="game-stats">
                <span>{{ game.viewers.toLocaleString('fr-FR') }} viewers</span>
                <span>/ {{ game.players.toLocaleString('fr-FR') }} joueurs</span>
              </div>
            </div>
            <div class="ratio-badge ratio-high">x{{ game.hype_ratio }}</div>
          </div>
        </div>
      </section>

      <section class="section extreme-card">
        <h2 class="section-title title-silence">Joués en silence (Fidélité discrète)</h2>
        <p class="section-desc">Ces jeux rassemblent des communautés très actives mais peu regardées en stream.</p>
        <div class="game-list">
          <div v-for="game in playedInSilence" :key="game.appid" class="game-item">
            <img :src="game.header_image" :alt="game.name" class="game-cover" />
            <div class="game-info">
              <span class="game-name">{{ game.name }}</span>
              <div class="game-stats">
                <span>{{ game.viewers.toLocaleString('fr-FR') }} viewers</span>
                <span>/ {{ game.players.toLocaleString('fr-FR') }} joueurs</span>
              </div>
            </div>
            <div class="ratio-badge ratio-low">x{{ game.hype_ratio }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface HypeGame {
  appid: number
  name: string
  header_image: string
  viewers: number
  players: number
  hype_ratio: number
}

const watchedMore = ref<HypeGame[]>([
  {
    appid: 252490,
    name: 'Rust',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/252490/header.jpg',
    viewers: 140000,
    players: 65000,
    hype_ratio: 2.15
  },
  {
    appid: 1086940,
    name: 'Baldur\'s Gate 3',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/1086940/header.jpg',
    viewers: 95000,
    players: 55000,
    hype_ratio: 1.73
  }
])

const playedInSilence = ref<HypeGame[]>([
  {
    appid: 413150,
    name: 'Stardew Valley',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg',
    viewers: 3500,
    players: 85000,
    hype_ratio: 0.04
  },
  {
    appid: 289070,
    name: 'Civilization VI',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/289070/header.jpg',
    viewers: 1200,
    players: 52000,
    hype_ratio: 0.02
  }
])
</script>

<style scoped>
.hype-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
}
.page-header { margin-bottom: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem; }
.title { font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.subtitle { color: #4b5563; margin: 0; }
.extremes-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }
.extreme-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  background: #fff;
}
.section-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.5rem 0; }
.title-watched { color: #9333ea; }
.title-silence { color: #0284c7; }
.section-desc { font-size: 0.875rem; color: #6b7280; margin: 0 0 1.25rem 0; line-height: 1.4; }
.game-list { display: flex; flex-direction: column; gap: 0.75rem; }
.game-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border: 1px solid #f3f4f6;
  border-radius: 0.5rem;
  background: #f9fafb;
}
.game-cover { width: 60px; height: 32px; object-fit: cover; border-radius: 0.25rem; }
.game-info { flex: 1; display: flex; flex-direction: column; }
.game-name { font-weight: 600; font-size: 0.95rem; }
.game-stats { font-size: 0.75rem; color: #6b7280; }
.ratio-badge {
  font-weight: 800;
  font-size: 0.85rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}
.ratio-high { background: #f3e8ff; color: #7e22ce; }
.ratio-low { background: #e0f2fe; color: #0369a1; }
</style>
