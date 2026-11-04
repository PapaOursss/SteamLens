<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4 text-center">
      <h1 class="text-2xl font-bold text-white tracking-tight">Mini-jeu : Plus ou Moins</h1>
      <p class="text-sm text-slate-400 mt-1">Défiez vos intuitions sur les statistiques de Steam !</p>
      <div class="mt-3 flex justify-center gap-3">
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300">
          Score : {{ score }}
        </span>
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/60 border border-amber-800 text-amber-300">
          Série max : {{ bestStreak }}
        </span>
      </div>
    </header>

    <div v-if="loading" class="text-center py-12 text-sm text-slate-400">
      Chargement du prochain duel...
    </div>

    <div v-else class="space-y-6">
      <div class="text-center py-2 px-4 rounded-lg bg-cyan-950/40 border border-cyan-800/60 text-cyan-300 text-sm font-medium max-w-md mx-auto">
        Métrique : <strong class="text-cyan-200">{{ metricLabel }}</strong>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-center gap-6">
        <!-- Game A -->
        <div class="w-72 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg pb-4 text-center">
          <img :src="gameA.header_image" :alt="gameA.name" class="w-full h-36 object-cover" />
          <h2 class="font-bold text-base text-white p-3 truncate">{{ gameA.name }}</h2>
          <div class="px-3 py-2 mx-4 rounded-lg bg-slate-950 border border-slate-800 text-sm font-semibold text-cyan-400">
            {{ formatMetricValue(gameA[currentMetric]) }}
          </div>
        </div>

        <div class="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-black text-slate-300 shadow">
          VS
        </div>

        <!-- Game B -->
        <div class="w-72 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg pb-4 text-center">
          <img :src="gameB.header_image" :alt="gameB.name" class="w-full h-36 object-cover" />
          <h2 class="font-bold text-base text-white p-3 truncate">{{ gameB.name }}</h2>

          <div v-if="!revealed" class="flex flex-col gap-2 px-4">
            <button
              class="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors shadow"
              @click="handleGuess(true)"
            >
              ▲ Plus élevé
            </button>
            <button
              class="w-full py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-colors shadow"
              @click="handleGuess(false)"
            >
              ▼ Moins élevé
            </button>
          </div>

          <div
            v-else
            class="mx-4 p-3 rounded-lg border flex flex-col gap-1.5"
            :class="isCorrect ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300' : 'bg-rose-950/60 border-rose-800 text-rose-300'"
          >
            <span class="text-sm font-bold">{{ formatMetricValue(gameB[currentMetric]) }}</span>
            <span class="text-xs font-semibold">{{ isCorrect ? 'Bien vu !' : 'Raté !' }}</span>
            <button
              class="mt-1 py-1.5 px-3 rounded bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
              @click="loadNextDuel"
            >
              Suivant →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

useHead({
  title: 'Duel de jeux — SteamLens'
})

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
  return "Pourcentage d'avis positifs"
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
