<template>
  <div class="space-y-8">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Ventes par Région (Kaggle vgsales)</h1>
      <p class="text-sm text-slate-400 mt-1">
        Comparaison des préférences culturelles et genres préférés : Amérique du Nord, Europe, Japon et Reste du Monde.
      </p>
    </header>

    <!-- Mini-carte interactive du monde -->
    <section class="space-y-3">
      <div class="flex items-center gap-2">
        <h2 class="text-base font-bold text-slate-100">Carte interactive des ventes mondiales</h2>
        <span class="bg-indigo-950 text-indigo-400 text-xs font-semibold px-2 py-0.5 rounded-full border border-indigo-800/60 uppercase">Interactif</span>
      </div>
      <RegionalSalesMap />
    </section>

    <!-- Bannière synthétique des préférences -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-1 shadow-sm">
        <span class="text-xs text-slate-400 font-medium">🇺🇸 / 🇨🇦 Amérique du Nord</span>
        <strong class="text-base font-bold text-white">Action & Tir (Shooter)</strong>
        <p class="text-xs text-slate-400 mt-1">Marché orienté blockbusters AAA et multijoueur compétitif.</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-1 shadow-sm">
        <span class="text-xs text-slate-400 font-medium">🇪🇺 Europe</span>
        <strong class="text-base font-bold text-white">Action & Sports</strong>
        <p class="text-xs text-slate-400 mt-1">Domination marquée des simulations de football et sports mécaniques.</p>
      </div>
      <div class="bg-slate-900 border border-pink-900/60 rounded-xl p-4 flex flex-col gap-1 shadow-sm bg-gradient-to-br from-slate-900 to-pink-950/20">
        <span class="text-xs text-pink-400 font-medium">🇯🇵 Japon</span>
        <strong class="text-base font-bold text-pink-300">Jeux de Rôle (J-RPG)</strong>
        <p class="text-xs text-slate-400 mt-1">Unique au monde : le RPG dépasse tous les autres genres réunis.</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-1 shadow-sm">
        <span class="text-xs text-slate-400 font-medium">🌐 Reste du Monde</span>
        <strong class="text-base font-bold text-white">Action & Sports</strong>
        <p class="text-xs text-slate-400 mt-1">Forte diffusion des franchises universelles (GTA, FIFA).</p>
      </div>
    </section>

    <!-- Tableau détaillé par genre -->
    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Volumes de ventes par genre (Millions d'unités)</h2>
      <div class="overflow-x-auto border border-slate-800 rounded-lg">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="bg-slate-950 text-slate-300 border-b border-slate-800 text-xs">
              <th class="p-3">Genre</th>
              <th class="p-3">Amérique du Nord</th>
              <th class="p-3">Europe</th>
              <th class="p-3">Japon</th>
              <th class="p-3">Total Mondial</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 text-slate-200">
            <tr v-for="item in salesData" :key="item.genre" class="hover:bg-slate-850/50">
              <td class="p-3 font-semibold text-slate-100">{{ item.genre }}</td>
              <td class="p-3 text-slate-300">{{ item.na }} M</td>
              <td class="p-3 text-slate-300">{{ item.eu }} M</td>
              <td class="p-3 font-medium" :class="item.genre === 'Role-Playing' ? 'text-pink-400 font-bold' : 'text-slate-300'">
                {{ item.jp }} M
              </td>
              <td class="p-3 font-bold text-slate-100">{{ (item.na + item.eu + item.jp).toFixed(1) }} M</td>
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

useHead({
  title: 'Ventes par Région — SteamLens'
})

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
