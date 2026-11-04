<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Laboratoire d'Expérimentations</h1>
      <p class="text-sm text-slate-400 mt-1">
        Visualisations alternatives, mini-jeux et modules d'analyse transversaux.
      </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <article
        v-for="exp in experiments"
        :key="exp.to"
        class="flex flex-col justify-between p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/50 transition-all shadow-md group"
      >
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
              {{ exp.tag }}
            </span>
            <span class="text-slate-400 text-xs">T-{{ exp.task }}</span>
          </div>
          <h2 class="text-base font-bold text-white group-hover:text-cyan-400 transition-colors">
            {{ exp.title }}
          </h2>
          <p class="text-xs text-slate-400 mt-2 leading-relaxed">
            {{ exp.description }}
          </p>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <span class="text-xs text-slate-400">Source : {{ exp.source }}</span>
          <NuxtLink
            :to="exp.to"
            class="text-xs font-medium text-cyan-400 hover:underline flex items-center gap-1"
          >
            Lancer →
          </NuxtLink>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Labo — SteamLens'
})

const experiments = [
  {
    title: 'Steam Deck & Proton',
    description: 'Statut de compatibilité ProtonDB et validation des tiers Linux (Gold, Platinum).',
    tag: 'Hardware',
    task: '38',
    source: 'ProtonDB',
    to: '/steam-deck'
  },
  {
    title: 'Durée de vie & Rentabilité',
    description: 'Calcul du coût par heure jouée et temps médian par genre.',
    tag: 'Gameplay',
    task: '39',
    source: 'Kaggle & HowLongToBeat',
    to: '/playtime'
  },
  {
    title: 'Duel de jeux',
    description: 'Devinez quel jeu réunit le plus de joueurs ou le meilleur score Metacritic.',
    tag: 'Mini-jeu',
    task: '40',
    source: 'Steam Web API',
    to: '/minigame'
  },
  {
    title: 'Steam Wrapped Annuel',
    description: 'Cartes interactives retraçant les moments forts et records de l\'année Steam.',
    tag: 'Rétrospective',
    task: '43',
    source: 'Catalogue global',
    to: '/wrapped'
  },
  {
    title: 'Ventes régionales',
    description: 'Part de marché globale et distribution historique des ventes (VGChartz).',
    tag: 'Économie',
    task: '44',
    source: 'VGChartz Kaggle',
    to: '/regional-sales'
  },
  {
    title: 'Twitch Hype vs Joueurs',
    description: 'Comparaison entre spectateurs Twitch et joueurs Steam réels.',
    tag: 'Streaming',
    task: '34',
    source: 'Twitch Helix',
    to: '/hype'
  }
]
</script>
