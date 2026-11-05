<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Durée de vie des jeux & Rentabilité</h1>
      <p class="text-sm text-slate-400 mt-1">
        Analyse du temps de jeu médian par genre et classement des jeux offrant le meilleur coût par heure de jeu.
      </p>
    </header>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Temps de jeu médian par genre</h2>
      <div class="flex flex-col gap-3">
        <div v-for="item in genreMedians" :key="item.genre" class="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
          <div class="flex justify-between items-center text-xs mb-1.5">
            <span class="font-semibold text-slate-200">{{ item.genre }}</span>
            <span class="font-bold text-cyan-400">{{ item.median_hours }} heures</span>
          </div>
          <div class="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
              :style="{ width: `${Math.min(100, (item.median_hours / maxHours) * 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Top 5 Rentabilité : Prix par heure jouée</h2>
      <div class="overflow-x-auto border border-slate-800 rounded-lg">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="bg-slate-950 text-slate-300 border-b border-slate-800 text-xs">
              <th class="p-3">Jeu</th>
              <th class="p-3">Temps médian</th>
              <th class="p-3">Prix</th>
              <th class="p-3">Coût / heure</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 text-slate-200">
            <tr v-for="game in bestValue" :key="game.appid" class="hover:bg-slate-850/50">
              <td class="p-3 flex items-center gap-3">
                <img :src="game.header_image" :alt="game.name" class="w-14 h-7 object-cover rounded" />
                <span class="font-semibold text-slate-100">{{ game.name }}</span>
              </td>
              <td class="p-3 text-slate-300">{{ game.median_hours }} h</td>
              <td class="p-3 text-slate-300">{{ game.price_eur > 0 ? `${game.price_eur.toFixed(2)} €` : 'Gratuit' }}</td>
              <td class="p-3 font-bold text-emerald-400">{{ game.cost_per_hour.toFixed(2) }} €/h</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

useHead({
  title: 'Durée de vie & Rentabilité — SteamLens'
})

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
    name: "Sid Meier's Civilization VI",
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
