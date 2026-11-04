<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Compatibilité Linux & Steam Deck (ProtonDB)</h1>
      <p class="text-sm text-slate-400 mt-1">
        Analyse de la jouabilité de la bibliothèque Steam sous Linux et Steam Deck grâce aux retours communautaires ProtonDB.
      </p>
    </header>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
      <h2 class="text-base font-bold text-slate-100">Répartition globale des niveaux</h2>
      <div class="flex flex-wrap gap-3">
        <ProtonBadge tier="native" :total-reports="120" />
        <ProtonBadge tier="platinum" :score="0.95" :total-reports="450" />
        <ProtonBadge tier="gold" :score="0.82" :total-reports="320" />
        <ProtonBadge tier="silver" :score="0.65" :total-reports="180" />
        <ProtonBadge tier="bronze" :score="0.45" :total-reports="90" />
        <ProtonBadge tier="borked" :score="0.10" :total-reports="40" />
      </div>
    </section>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Répartition par genre</h2>
      <div class="overflow-x-auto border border-slate-800 rounded-lg">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="bg-slate-950 text-slate-300 border-b border-slate-800 text-xs">
              <th class="p-3">Genre</th>
              <th class="p-3">Platinum</th>
              <th class="p-3">Gold</th>
              <th class="p-3">Silver</th>
              <th class="p-3">Bronze</th>
              <th class="p-3">Borked</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 text-slate-200">
            <tr v-for="item in genreBreakdown" :key="item.genre" class="hover:bg-slate-850/50">
              <td class="p-3 font-semibold text-slate-100">{{ item.genre }}</td>
              <td class="p-3 text-indigo-400 font-medium">{{ item.counts.platinum }}</td>
              <td class="p-3 text-amber-400 font-medium">{{ item.counts.gold }}</td>
              <td class="p-3 text-slate-400 font-medium">{{ item.counts.silver }}</td>
              <td class="p-3 text-orange-400 font-medium">{{ item.counts.bronze }}</td>
              <td class="p-3 text-rose-400 font-medium">{{ item.counts.borked }}</td>
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

useHead({
  title: 'Steam Deck & ProtonDB — SteamLens'
})

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
