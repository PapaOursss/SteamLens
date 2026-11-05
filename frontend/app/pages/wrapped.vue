<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4 text-center">
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-pink-950/60 text-pink-400 border border-pink-800/60 mb-2">
        SteamLens Rewind
      </span>
      <h1 class="text-3xl font-extrabold text-white tracking-tight">Steam Wrapped {{ year }}</h1>
      <p class="text-sm text-slate-400 mt-1">L'année du jeu vidéo résumée en cartes interactives.</p>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <article class="bg-gradient-to-br from-slate-900 to-slate-950 border border-cyan-800/50 rounded-xl p-5 shadow-lg flex flex-col items-center text-center">
        <span class="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 mb-2">
          Jeu de l'année
        </span>
        <img :src="wrappedData.game_of_the_year.header_image" :alt="wrappedData.game_of_the_year.name" class="w-full h-32 object-cover rounded-lg my-2" />
        <h2 class="text-base font-bold text-white">{{ wrappedData.game_of_the_year.name }}</h2>
        <p class="text-xs text-slate-400 mt-1">
          Pic historique : <strong class="text-cyan-400">{{ wrappedData.game_of_the_year.peak_players.toLocaleString('fr-FR') }}</strong> joueurs
        </p>
      </article>

      <article class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col items-center text-center">
        <span class="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 mb-2">
          Genre en essor
        </span>
        <h2 class="text-base font-bold text-white mt-2">{{ wrappedData.trending_genre.name }}</h2>
        <div class="text-3xl font-extrabold text-emerald-400 my-2">+{{ wrappedData.trending_genre.growth_percent }}%</div>
        <p class="text-xs text-slate-400 leading-relaxed">
          Porté par le succès de <strong class="text-slate-200">{{ wrappedData.trending_genre.flagship_game }}</strong>.
        </p>
      </article>

      <article class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col items-center text-center">
        <span class="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 mb-2">
          Plus grosse promo
        </span>
        <h2 class="text-base font-bold text-white mt-2">{{ wrappedData.biggest_discount.name }}</h2>
        <div class="text-3xl font-extrabold text-amber-400 my-2">-{{ wrappedData.biggest_discount.discount_percent }}%</div>
        <p class="text-xs text-slate-400 leading-relaxed">
          Tombé à seulement <strong class="text-slate-200">{{ wrappedData.biggest_discount.final_price_eur.toFixed(2) }} €</strong> lors des soldes.
        </p>
      </article>

      <article class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col items-center text-center">
        <span class="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-800 mb-2">
          Le coup dur
        </span>
        <h2 class="text-base font-bold text-white mt-2">{{ wrappedData.biggest_flop.name }}</h2>
        <p class="text-xs text-slate-400 mt-3 leading-relaxed">{{ wrappedData.biggest_flop.reason }}</p>
      </article>

      <article class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col items-center text-center sm:col-span-2 lg:col-span-1">
        <span class="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-800 mb-2">
          Zone la plus chère
        </span>
        <h2 class="text-base font-bold text-white mt-2">{{ wrappedData.most_expensive_country.country }}</h2>
        <div class="text-3xl font-extrabold text-purple-400 my-2">+{{ wrappedData.most_expensive_country.premium_percent }}%</div>
        <p class="text-xs text-slate-400 leading-relaxed">{{ wrappedData.most_expensive_country.reason }}</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

useHead({
  title: 'Steam Wrapped — SteamLens'
})

const year = ref(2026)

const wrappedData = ref({
  game_of_the_year: {
    appid: 730,
    name: 'Counter-Strike 2',
    header_image: 'https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg',
    peak_players: 1420000
  },
  trending_genre: {
    name: 'Roguelike Deckbuilder',
    growth_percent: 145,
    flagship_game: 'Balatro'
  },
  biggest_discount: {
    name: 'The Witcher 3: Wild Hunt',
    discount_percent: 80,
    final_price_eur: 5.99
  },
  biggest_flop: {
    name: 'The Day Before',
    reason: "Retiré des ventes 4 jours après son lancement suite à 85% d'avis négatifs."
  },
  most_expensive_country: {
    country: 'Suisse (CHF)',
    premium_percent: 18.5,
    reason: 'Prix de base systématiquement ajustés au-dessus de la zone Euro.'
  }
})
</script>
