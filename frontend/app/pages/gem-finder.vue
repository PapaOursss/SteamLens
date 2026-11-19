<template>
  <div>
    <PageIntro title="Chercheur de pépites" is-lab>
      Trouvez des jeux très bien notés, accessibles en prix et encore méconnus. Cliquez sur un point pour ouvrir sa fiche.
    </PageIntro>

    <div class="gutter mb-6 flex flex-wrap items-center gap-4">
      <label class="flex flex-col text-sm text-soft">
        <span class="mb-1 font-semibold text-text">Genre</span>
        <select v-model="selectedGenre" class="rounded border border-line bg-deep px-3 py-1.5 text-text">
          <option value="">Tous les genres</option>
          <option v-for="g in data?.genres" :key="g" :value="g">{{ g }}</option>
        </select>
      </label>

      <label class="flex flex-col text-sm text-soft">
        <span class="mb-1 font-semibold text-text">Année de sortie</span>
        <select v-model="selectedYear" class="rounded border border-line bg-deep px-3 py-1.5 text-text">
          <option value="">Toutes les années</option>
          <option v-for="y in data?.years" :key="y" :value="y">{{ y }}</option>
        </select>
      </label>

      <label class="flex items-center gap-2 pt-5 text-sm text-text cursor-pointer">
        <input v-model="onlyGems" type="checkbox" class="accent-hot rounded" />
        <span>Uniquement les pépites (≤ 15 €, ≥ 85 % avis)</span>
      </label>
    </div>

    <DataBlock
      title="Nuage de points : Prix vs Avis positifs"
      note="Taille du point = estimation des possesseurs · Couleur = genre principal."
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

    <div v-if="selectedGame" class="gutter mt-8">
      <h3 class="mb-3 text-lg font-bold">Jeu sélectionné</h3>
      <div class="flex flex-wrap items-center gap-6 rounded-lg border border-line bg-deep/60 p-4">
        <GameCover
          :sources="wideCoverSources(selectedGame.appid, selectedGame.header_image)"
          :name="selectedGame.name"
          :width="230"
          :height="107"
          class="aspect-[460/215] w-[230px] shrink-0"
        />
        <div class="space-y-1">
          <NuxtLink :to="gameLink(selectedGame.appid)" class="text-xl font-bold text-text hover:text-hot link">
            {{ selectedGame.name }}
          </NuxtLink>
          <p class="text-sm text-soft">
            Genre : {{ selectedGame.genre }} · Année : {{ selectedGame.year || 'Non renseignée' }}
          </p>
          <p class="text-sm text-soft">
            Prix : {{ selectedGame.price_eur > 0 ? `${selectedGame.price_eur} €` : 'Gratuit' }} ·
            Avis positifs : <strong class="text-hot">{{ selectedGame.positive_percent }} %</strong> ·
            Possesseurs estimés : ~{{ formatCompact(selectedGame.owners) }}
          </p>
        </div>
      </div>
    </div>
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
