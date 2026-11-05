<template>
  <div>
    <PageIntro title="Les jeux suivis">
      {{ page ? `${formatNumber(page.count)} jeux` : 'Le catalogue' }} de SteamLens, à chercher par nom ou à filtrer par genre.
    </PageIntro>

    <div class="gutter mb-6 space-y-3">
      <label class="flex min-h-11 max-w-md items-center gap-2 rounded-md bg-deep px-3 focus-within:outline focus-within:outline-[3px] focus-within:outline-offset-2 focus-within:outline-hot">
        <span class="shrink-0 text-soft">Nom</span>
        <input v-model="searchText" type="search" class="min-w-0 flex-1 bg-transparent py-2 outline-none">
      </label>
      <div role="group" aria-label="Filtrer par genre" class="-mx-4 flex gap-1 overflow-x-auto px-4 md:mx-0 md:flex-wrap md:px-0">
        <NuxtLink
          v-for="option in genreOptions"
          :key="option.label"
          :to="{ query: linkQuery({ genre: option.value, page: undefined }) }"
          class="inline-flex min-h-11 shrink-0 items-center rounded-md px-3"
          :class="option.value === genre ? 'bg-hot font-medium text-deep' : 'bg-deep text-soft hover:text-text'"
        >
          {{ option.label }}
        </NuxtLink>
      </div>
    </div>

    <div v-if="isLoading" class="aspect-[2/1] animate-pulse bg-deep motion-reduce:animate-none" />
    <div v-else-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Le catalogue n'arrive pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="refresh()">Réessayer</button>
    </div>
    <p v-else-if="!page?.results.length" class="gutter bg-deep py-8 text-soft">Aucun jeu ne correspond.</p>
    <ul v-else class="grid grid-cols-2 gap-px md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6">
      <li v-for="game in page.results" :key="game.appid">
        <GameTile :appid="game.appid" :name="game.name" :header-image="game.header_image">
          <template v-if="game.is_free">Gratuit</template>
        </GameTile>
      </li>
    </ul>

    <nav v-if="page && pageCount > 1" aria-label="Pages" class="gutter mt-6 flex items-center gap-3">
      <NuxtLink v-if="pageNumber > 1" class="button-quiet" :to="{ query: linkQuery({ page: pageNumber - 1 }) }">Précédents</NuxtLink>
      <span class="figure text-soft">Page {{ formatNumber(pageNumber) }} sur {{ formatNumber(pageCount) }}</span>
      <NuxtLink v-if="pageNumber < pageCount" class="button-quiet" :to="{ query: linkQuery({ page: pageNumber + 1 }) }">Suivants</NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import type { GameListItem, GenreStat, PaginatedResponse } from '~/types'

type ListQuery = Record<string, string | number | undefined>

const PAGE_SIZE = 48
const SEARCH_DELAY_MS = 300

useHead({ title: 'Jeux' })

const route = useRoute()
const genre = computed(() => (route.query.genre as string | undefined) ?? undefined)
const search = computed(() => (route.query.search as string | undefined) ?? '')
const pageNumber = computed(() => Number(route.query.page) || 1)

function linkQuery(changes: ListQuery): ListQuery {
  return { ...route.query, ...changes } as ListQuery
}

const { data: page, isLoading, hasError, refresh } = useApiResource<PaginatedResponse<GameListItem>>(
  '/games/',
  () => ({ search: search.value || undefined, genre: genre.value, page: pageNumber.value, page_size: PAGE_SIZE })
)
const { data: genres } = useApiResource<GenreStat[]>('/stats/genres/')

const pageCount = computed(() => Math.ceil((page.value?.count ?? 0) / PAGE_SIZE))
const genreOptions = computed(() => [
  { label: 'Tous', value: undefined },
  ...(genres.value ?? []).map((item) => ({ label: item.name, value: item.name as string | undefined }))
])

const searchText = ref(search.value)
const settledSearch = useDebounced(searchText, SEARCH_DELAY_MS)

watch(settledSearch, (text) => {
  navigateTo({ query: linkQuery({ search: text || undefined, page: undefined }) }, { replace: true })
})
</script>
