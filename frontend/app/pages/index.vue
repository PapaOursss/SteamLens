<template>
  <div class="space-y-8">
    <!-- Hero Banner -->
    <section class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-cyan-950 border border-slate-800 p-6 sm:p-8 shadow-xl">
      <div class="relative z-10 max-w-3xl">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-3">
          ● Plateforme d'analyse Steam
        </span>
        <h1 class="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          Explorez l'écosystème du jeu vidéo avec SteamLens
        </h1>
        <p class="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed">
          Visualisez la popularité des jeux, l'évolution des prix à l'échelle mondiale, la compatibilité Steam Deck et les dynamiques communautaires à partir de plus de 10 sources unifiées.
        </p>

        <div class="mt-6 flex flex-wrap gap-3">
          <NuxtLink
            to="/hype"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold shadow-md transition-colors"
          >
            Voir les tendances
          </NuxtLink>
          <NuxtLink
            to="/sources"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold border border-slate-700 transition-colors"
          >
            Méthodologie & Sources
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Quick Stats & Chart Showcase -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ChartCard
        title="Distribution du catalogue"
        subtitle="Répartition des jeux par grands genres"
        source="Kaggle Steam Complete"
      >
        <div class="flex flex-col justify-center h-full space-y-3 py-2">
          <div v-for="item in sampleDistribution" :key="item.genre" class="space-y-1">
            <div class="flex justify-between text-xs">
              <span class="font-medium text-slate-300">{{ item.genre }}</span>
              <span class="text-slate-400">{{ item.count.toLocaleString('fr-FR') }} jeux</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                class="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full"
                :style="{ width: `${item.percentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </ChartCard>

      <ChartCard
        title="Temps réel des joueurs"
        subtitle="Snapshot CCU des titres phares"
        source="Steam Web API"
        :loading="isLoadingTop"
      >
        <div class="flex flex-col justify-center h-full space-y-3">
          <div class="text-center py-4">
            <span class="text-3xl font-extrabold text-cyan-400">14.8M</span>
            <p class="text-xs text-slate-400 mt-1">Joueurs connectés simultanés estimés</p>
          </div>
          <div class="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-slate-400">
            Mise à jour en continu via les snapshots planifiés du worker.
          </div>
        </div>
      </ChartCard>

      <ChartCard
        title="Historique des soldes"
        subtitle="Indice des prix réduits en temps réel"
        source="CheapShark / ITAD"
        empty
        empty-message="Aucune campagne de soldes globale active pour le moment."
      />
    </section>

    <!-- Navigation Hub -->
    <section class="space-y-4">
      <h2 class="text-lg font-bold text-slate-200">Modules d'exploration</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <NuxtLink
          v-for="hub in hubLinks"
          :key="hub.to"
          :to="hub.to"
          class="group p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900 transition-all shadow-sm"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">
              {{ hub.title }}
            </span>
            <span class="text-xs text-slate-400 group-hover:translate-x-1 transition-transform">→</span>
          </div>
          <p class="text-xs text-slate-400 line-clamp-2">
            {{ hub.description }}
          </p>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isLoadingTop = ref(false)

const sampleDistribution = [
  { genre: 'Action / Aventure', count: 28410, percentage: 85 },
  { genre: 'Indépendant', count: 24200, percentage: 72 },
  { genre: 'Stratégie', count: 12150, percentage: 36 },
  { genre: 'Jeu de rôle (RPG)', count: 9800, percentage: 29 },
  { genre: 'Simulation', count: 8400, percentage: 25 }
]

const hubLinks = [
  {
    title: 'Tendances & Twitch',
    description: 'Analyse comparative du buzz streaming face aux joueurs réels en jeu.',
    to: '/hype'
  },
  {
    title: 'Compatibilité Steam Deck',
    description: 'Suivi des validations ProtonDB et taux de compatibilité Linux.',
    to: '/steam-deck'
  },
  {
    title: 'Rentabilité par heure',
    description: 'Durée de vie médiane des jeux et ratio coût par heure jouée.',
    to: '/playtime'
  },
  {
    title: 'Steam Wrapped',
    description: 'Rétrospective annuelle stylisée des records et sorties marquantes.',
    to: '/wrapped'
  },
  {
    title: 'Ventes régionales',
    description: 'Part de marché par continent selon les données historiques globales.',
    to: '/regional-sales'
  },
  {
    title: 'Duel de jeux',
    description: 'Mini-jeu interactif pour tester vos connaissances des statistiques Steam.',
    to: '/minigame'
  }
]
</script>
