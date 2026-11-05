<template>
  <aside
    class="flex flex-col w-64 bg-slate-950 border-r border-slate-800 text-slate-200 transition-all duration-300 select-none"
  >
    <!-- Brand / Header -->
    <div class="flex items-center justify-between px-6 py-5 border-b border-slate-800/80">
      <NuxtLink to="/" class="flex items-center gap-3 group">
        <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-black text-lg shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
          SL
        </div>
        <div class="flex flex-col">
          <span class="font-bold text-base tracking-wide text-white group-hover:text-cyan-400 transition-colors">
            SteamLens
          </span>
          <span class="text-[10px] uppercase font-semibold tracking-wider text-slate-400">
            Observatoire Steam
          </span>
        </div>
      </NuxtLink>
    </div>

    <!-- Navigation List -->
    <nav class="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
      <div>
        <div class="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        <ul class="space-y-1">
          <li v-for="item in mainLinks" :key="item.to">
            <NuxtLink
              :to="item.to"
              class="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition-colors"
              active-class="!text-cyan-400 !bg-cyan-950/40 border border-cyan-800/40 font-semibold shadow-xs"
              @click="$emit('navigate')"
            >
              <component :is="item.icon" class="w-4 h-4 shrink-0" />
              <span>{{ item.label }}</span>
            </NuxtLink>
          </li>
        </ul>
      </div>

      <div>
        <div class="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Exploration
        </div>
        <ul class="space-y-1">
          <li v-for="item in labLinks" :key="item.to">
            <NuxtLink
              :to="item.to"
              class="flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors"
              active-class="!text-cyan-400 !bg-cyan-950/40 border border-cyan-800/40 font-semibold"
              @click="$emit('navigate')"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
              <span>{{ item.label }}</span>
            </NuxtLink>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Footer Meta -->
    <div class="p-4 border-t border-slate-800/80 text-[11px]">
      <NuxtLink to="/sources" class="text-slate-400 hover:text-cyan-400 transition-colors">
        Sources & Méthodologie
      </NuxtLink>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { h } from 'vue'

defineEmits<{
  (e: 'navigate'): void
}>()

function createSvgIcon(path: string) {
  return () =>
    h(
      'svg',
      {
        fill: 'none',
        viewBox: '0 0 24 24',
        strokeWidth: '1.75',
        stroke: 'currentColor',
        xmlns: 'http://www.w3.org/2000/svg'
      },
      [h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', d: path })]
    )
}

const icons = {
  home: createSvgIcon('M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'),
  game: createSvgIcon('M15 6v2a3 3 0 003 3h2a2 2 0 012 2v2a6 6 0 01-6 6H8a6 6 0 01-6-6v-2a2 2 0 012-2h2a3 3 0 003-3V6a2 2 0 012-2h2a2 2 0 012 2zm-8 7h4m-2-2v4m7-2h.01m3-2h.01'),
  genre: createSvgIcon('M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z'),
  globe: createSvgIcon('M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9'),
  price: createSvgIcon('M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'),
  trend: createSvgIcon('M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'),
  lab: createSvgIcon('M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z')
}

const mainLinks = [
  { label: 'Accueil', to: '/', icon: icons.home },
  { label: 'Jeux', to: '/games', icon: icons.game },
  { label: 'Genres', to: '/genres', icon: icons.genre },
  { label: 'Monde', to: '/world', icon: icons.globe },
  { label: 'Prix', to: '/pricing', icon: icons.price },
  { label: 'Tendances', to: '/hype', icon: icons.trend },
  { label: 'Labo', to: '/lab', icon: icons.lab }
]

const labLinks = [
  { label: 'Steam Deck', to: '/steam-deck' },
  { label: 'Durée de vie', to: '/playtime' },
  { label: 'Duel de jeux', to: '/minigame' },
  { label: 'Steam Wrapped', to: '/wrapped' },
  { label: 'Ventes régionales', to: '/regional-sales' },
  { label: 'Historique des prix', to: '/price-history' },
  { label: 'Avis & bombings', to: '/reviews' },
  { label: 'Matériel des joueurs', to: '/hardware' },
  { label: 'Succès jamais finis', to: '/achievements' },
  { label: 'Pays des profils', to: '/profile-map' },
  { label: 'Sources de données', to: '/sources' }
]
</script>
