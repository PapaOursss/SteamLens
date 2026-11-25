<template>
  <div>
    <PageIntro title="Chercheur de pépites" is-lab>
      Des jeux très bien notés, peu chers et encore méconnus. Cliquez sur un point pour le voir en détail.
    </PageIntro>

    <SampleNotice v-if="data?.is_sample" class="mb-6">
      Les prix et les avis n'ont pas encore été importés : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <div class="gutter mb-6 flex flex-wrap items-center gap-4">
      <label class="flex flex-col gap-1 text-sm text-soft">
        Genre
        <select v-model="selectedGenre" class="field">
          <option value="">Tous les genres</option>
          <option v-for="g in data?.genres" :key="g" :value="g">{{ g }}</option>
        </select>
      </label>

      <label class="flex flex-col gap-1 text-sm text-soft">
        Année de sortie
        <select v-model="selectedYear" class="field">
          <option value="">Toutes les années</option>
          <option v-for="y in data?.years" :key="y" :value="y">{{ y }}</option>
        </select>
      </label>

      <label class="flex min-h-11 cursor-pointer items-center gap-2 self-end">
        <input v-model="onlyGems" type="checkbox" class="h-5 w-5 accent-hot">
        Seulement les pépites
      </label>
    </div>

    <DataBlock
      title="Prix et avis positifs"
      :note="gemNote"
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!filteredGames.length"
      empty-message="Aucun jeu ne correspond aux filtres sélectionnés."
      :height="560"
      @retry="refresh()"
    >
      <GemFinderChart
        v-if="data"
        :games="filteredGames"
        :criteria="data.gem_criteria"
        label="Nuage de points prix et avis positifs des jeux Steam"
        @select="onSelectGame"
      />
    </DataBlock>

    <section v-if="selectedGame" class="gutter mt-8" aria-live="polite">
      <h2 class="mb-3 text-2xl">Jeu sélectionné</h2>
      <div class="flex flex-wrap items-center gap-6 bg-deep p-4">
        <GameCover
          :sources="wideCoverSources(selectedGame.appid, selectedGame.header_image)"
          :name="selectedGame.name"
          :width="230"
          :height="107"
          class="aspect-[460/215] w-[230px] shrink-0"
        />
        <div class="space-y-1">
          <NuxtLink :to="gameLink(selectedGame.appid)" class="link font-display text-xl font-bold">
            {{ selectedGame.name }}
          </NuxtLink>
          <p class="text-soft">
            {{ selectedGame.genre }} · {{ selectedGame.year || 'année inconnue' }}
          </p>
          <p class="figure">
            {{ selectedGame.price_eur > 0 ? formatPrice(selectedGame.price_eur) : 'Gratuit' }} ·
            <strong>{{ formatPercent(selectedGame.positive_percent) }}</strong> d'avis positifs ·
            ~{{ formatCompact(selectedGame.owners) }} possesseurs
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { GemFinderGame, GemFinderResponse } from '~/types'

useHead({ title: 'Chercheur de pépites' })

const selectedGenre = ref('')
const selectedYear = ref<number | ''>('')
const onlyGems = ref(false)
const selectedGame = ref<GemFinderGame | null>(null)

const { data, isLoading, hasError, refresh } = useApiResource<GemFinderResponse>('/stats/gem-finder/')

const gemNote = computed(() => {
  const criteria = data.value?.gem_criteria
  const rule = criteria
    ? `Pépite : ${formatPrice(criteria.max_price)} au plus, ${formatPercent(criteria.min_score)} d'avis positifs au moins, ${formatCompact(criteria.max_owners)} possesseurs au plus. `
    : ''
  return `${rule}Prix français, sinon américain converti en euros. Taille du point : possesseurs estimés.`
})

const filteredGames = computed(() => {
  if (!data.value?.games) return []
  return data.value.games.filter((g) => {
    if (selectedGenre.value && g.genre !== selectedGenre.value) return false
    if (selectedYear.value !== '' && g.year !== Number(selectedYear.value)) return false
    if (onlyGems.value && !g.is_gem) return false
    return true
  })
})

function onSelectGame(game: GemFinderGame) {
  selectedGame.value = game
}
</script>
