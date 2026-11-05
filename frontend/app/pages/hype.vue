<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Hype contre Réalité : Twitch vs Steam</h1>
      <p class="text-sm text-slate-400 mt-1">
        Comparaison entre l'audience Twitch (spectateurs) et la fréquentation réelle Steam (joueurs en jeu).
      </p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 class="text-base font-bold text-purple-400 mb-1">Regardés plus que joués (Hype forte)</h2>
        <p class="text-xs text-slate-400 mb-4">Ces jeux attirent proportionnellement beaucoup plus de spectateurs que de joueurs actifs.</p>
        <div class="flex flex-col gap-2.5">
          <div v-for="game in watchedMore" :key="game.appid" class="flex items-center gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800/80">
            <img :src="game.header_image" :alt="game.name" class="w-16 h-8 object-cover rounded" />
            <div class="flex-1 min-w-0">
              <span class="font-semibold text-sm text-slate-100 truncate block">{{ game.name }}</span>
              <div class="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                <span>{{ game.viewers.toLocaleString('fr-FR') }} viewers</span>
                <span>/</span>
                <span>{{ game.players.toLocaleString('fr-FR') }} joueurs</span>
              </div>
            </div>
            <div class="font-bold text-xs px-2.5 py-1 rounded bg-purple-950 text-purple-300 border border-purple-800">
              x{{ game.hype_ratio }}
            </div>
          </div>
        </div>
      </section>

      <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 class="text-base font-bold text-cyan-400 mb-1">Joués en silence (Fidélité discrète)</h2>
        <p class="text-xs text-slate-400 mb-4">Ces jeux rassemblent des communautés très actives mais peu regardées en stream.</p>
        <div class="flex flex-col gap-2.5">
          <div v-for="game in playedInSilence" :key="game.appid" class="flex items-center gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800/80">
            <img :src="game.header_image" :alt="game.name" class="w-16 h-8 object-cover rounded" />
            <div class="flex-1 min-w-0">
              <span class="font-semibold text-sm text-slate-100 truncate block">{{ game.name }}</span>
              <div class="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                <span>{{ game.viewers.toLocaleString('fr-FR') }} viewers</span>
                <span>/</span>
                <span>{{ game.players.toLocaleString('fr-FR') }} joueurs</span>
              </div>
            </div>
            <div class="font-bold text-xs px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              x{{ game.hype_ratio }}
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

useHead({
  title: 'Hype Twitch vs Steam — SteamLens'
})

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
    name: "Baldur's Gate 3",
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
