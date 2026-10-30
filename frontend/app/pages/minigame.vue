<template>
  <div class="minigame-container">
    <header class="game-header">
      <h1 class="title">Mini-jeu : Plus ou Moins</h1>
      <p class="subtitle">Défiez vos intuitions sur les statistiques de Steam !</p>
      <div class="scoreboard">
        <span class="score-pill">Score : {{ score }}</span>
        <span class="score-pill streak-pill">Série max : {{ bestStreak }}</span>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      Chargement du prochain duel...
    </div>

    <div v-else class="duel-arena">
      <div class="metric-banner">
        Métrique : <strong>{{ metricLabel }}</strong>
      </div>

      <div class="cards-wrapper">
        <div class="game-card card-reference">
          <img :src="gameA.header_image" :alt="gameA.name" class="game-cover" />
          <h2 class="game-title">{{ gameA.name }}</h2>
          <div class="metric-value-box">
            <span class="value-text">{{ formatMetricValue(gameA[currentMetric]) }}</span>
          </div>
        </div>

        <div class="vs-badge">VS</div>

        <div class="game-card card-target">
          <img :src="gameB.header_image" :alt="gameB.name" class="game-cover" />
          <h2 class="game-title">{{ gameB.name }}</h2>

          <div v-if="!revealed" class="choices-actions">
            <button class="btn btn-higher" @click="handleGuess(true)">
              ▲ Plus élevé
            </button>
            <button class="btn btn-lower" @click="handleGuess(false)">
              ▼ Moins élevé
            </button>
          </div>

          <div v-else class="metric-value-box result-box" :class="isCorrect ? 'box-win' : 'box-loss'">
            <span class="value-text">{{ formatMetricValue(gameB[currentMetric]) }}</span>
            <span class="result-label">{{ isCorrect ? 'Bien vu !' : 'Raté !' }}</span>
            <button class="btn btn-next" @click="loadNextDuel">Suivant →</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface GameCardData {
  appid: number
  name: string
  header_image: string
  players: number
  price_eur: number
  review_score: number
  [key: string]: number | string
}

type MetricKey = 'players' | 'price_eur' | 'review_score'

const loading = ref(false)
const revealed = ref(false)
const isCorrect = ref(false)
const score = ref(0)
const bestStreak = ref(0)
const currentStreak = ref(0)
const currentMetric = ref<MetricKey>('players')

const gameA = ref<GameCardData>({
  appid: 730,
  name: 'Counter-Strike 2',
  header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg',
  players: 1250000,
  price_eur: 0.0,
  review_score: 88
})

const gameB = ref<GameCardData>({
  appid: 570,
  name: 'Dota 2',
  header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/570/header.jpg',
  players: 650000,
  price_eur: 0.0,
  review_score: 82
})

const metricLabel = computed(() => {
  if (currentMetric.value === 'players') return 'Nombre de joueurs en ligne'
  if (currentMetric.value === 'price_eur') return 'Prix en euros'
  return 'Pourcentage d\'avis positifs'
})

function formatMetricValue(val: number | string): string {
  const num = typeof val === 'number' ? val : parseFloat(val)
  if (currentMetric.value === 'players') return `${num.toLocaleString('fr-FR')} joueurs`
  if (currentMetric.value === 'price_eur') return num === 0 ? 'Gratuit' : `${num.toFixed(2)} €`
  return `${num} % positifs`
}

function handleGuess(guessHigher: boolean) {
  const valA = Number(gameA.value[currentMetric.value])
  const valB = Number(gameB.value[currentMetric.value])
  const win = guessHigher ? valB >= valA : valB <= valA

  isCorrect.value = win
  revealed.value = true

  if (win) {
    score.value += 1
    currentStreak.value += 1
    if (currentStreak.value > bestStreak.value) bestStreak.value = currentStreak.value
  } else {
    currentStreak.value = 0
  }
}

async function loadNextDuel() {
  loading.value = true
  revealed.value = false
  const metrics: MetricKey[] = ['players', 'price_eur', 'review_score']
  currentMetric.value = metrics[Math.floor(Math.random() * metrics.length)]
  loading.value = false
}

onMounted(() => {
  loadNextDuel()
})
</script>

<style scoped>
.minigame-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
  text-align: center;
}
.game-header { margin-bottom: 2rem; }
.title { font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.subtitle { color: #6b7280; margin: 0 0 1rem 0; }
.scoreboard { display: flex; justify-content: center; gap: 1rem; }
.score-pill {
  background: #f3f4f6;
  padding: 0.35rem 0.9rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.9rem;
}
.streak-pill { background: #fef3c7; color: #b45309; }
.metric-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}
.cards-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.game-card {
  width: 320px;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  background: #fff;
  padding-bottom: 1.5rem;
}
.game-cover { width: 100%; height: 160px; object-fit: cover; }
.game-title { font-size: 1.25rem; font-weight: 700; padding: 1rem 1rem 0.5rem 1rem; margin: 0; }
.vs-badge {
  font-size: 1.5rem;
  font-weight: 900;
  color: #9ca3af;
  background: #f3f4f6;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.metric-value-box {
  background: #f9fafb;
  padding: 1rem;
  margin: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  font-weight: 800;
}
.choices-actions { display: flex; flex-direction: column; gap: 0.5rem; padding: 0.5rem 1rem; }
.btn {
  border: none;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-weight: 700;
  font-size: 1rem;
  transition: opacity 0.2s;
}
.btn:hover { opacity: 0.9; }
.btn-higher { background: #22c55e; color: #fff; }
.btn-lower { background: #ef4444; color: #fff; }
.btn-next { background: #2563eb; color: #fff; margin-top: 0.5rem; }
.box-win { background: #dcfce7; color: #15803d; }
.box-loss { background: #fee2e2; color: #b91c1c; }
.result-box { display: flex; flex-direction: column; gap: 0.4rem; }
.result-label { font-size: 0.9rem; font-weight: 700; text-transform: uppercase; }
</style>
