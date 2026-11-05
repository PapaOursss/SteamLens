<template>
  <header class="gutter relative z-30 flex flex-wrap items-center gap-x-6 gap-y-2 py-3">
    <NuxtLink to="/" class="inline-flex min-h-11 items-center font-display text-2xl font-extrabold tracking-tight">
      SteamLens
    </NuxtLink>

    <nav ref="navigation" aria-label="Navigation principale" class="-mx-4 order-3 flex w-[calc(100%+2rem)] gap-1 overflow-x-auto px-4 lg:order-none lg:mx-0 lg:w-auto lg:px-0">
      <NuxtLink
        v-for="item in NAV_ITEMS"
        :key="item.to"
        :to="item.to"
        class="inline-flex min-h-11 shrink-0 items-center rounded-md px-3 font-medium"
        :class="isActive(item) ? 'bg-hot text-deep' : 'text-soft hover:text-text'"
        :aria-current="isActive(item) ? 'page' : undefined"
      >
        {{ item.label }}
      </NuxtLink>
    </nav>

    <GameSearch class="ml-auto w-full sm:w-72 lg:w-80" field-id="recherche-globale" @select="openGame" />
  </header>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'

interface NavItem {
  label: string
  to: string
  sections?: string[]
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Ce qui se joue', to: '/' },
  { label: 'Jeux', to: '/games' },
  { label: 'Genres', to: '/genres' },
  { label: 'Monde', to: '/world' },
  { label: 'Prix', to: '/pricing' },
  { label: 'Tendances', to: '/hype' },
  {
    label: 'Labo',
    to: '/lab',
    sections: ['/steam-deck', '/playtime', '/minigame', '/wrapped', '/regional-sales']
  }
]

const route = useRoute()
const navigation = useTemplateRef<HTMLElement>('navigation')

/** Sur téléphone, le menu défile : garde l'entrée de la page courante visible. */
function revealActiveItem() {
  navigation.value?.querySelector('[aria-current="page"]')?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
}

onMounted(revealActiveItem)
watch(() => route.path, () => nextTick(revealActiveItem))

function isActive(item: NavItem): boolean {
  if (item.to === '/') return route.path === '/'
  return [item.to, ...(item.sections ?? [])].some((path) => route.path.startsWith(path))
}

function openGame(game: GameOption) {
  navigateTo(gameLink(game.appid))
}
</script>
