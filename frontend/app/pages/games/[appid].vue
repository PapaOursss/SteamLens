<template>
  <div>
    <div v-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Ce jeu n'arrive pas : il n'est pas suivi, ou l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="refresh()">Réessayer</button>
    </div>
    <div v-else-if="!game" class="aspect-[3/1] animate-pulse bg-deep motion-reduce:animate-none" />
    <template v-else>
      <PageIntro :title="game.name">
        <template #under-title>
          <p class="mt-4 text-lg text-soft">{{ subtitle }}</p>
        </template>
        <GameCover
          :key="game.appid"
          :sources="wideCoverSources(game.appid, game.header_image)"
          :name="game.name"
          :width="460"
          :height="215"
          is-priority
          class="aspect-[460/215] h-auto w-full max-w-md"
        />
        <p v-if="game.short_description" class="mt-4">{{ game.short_description }}</p>
      </PageIntro>

      <GameFacts :game="game" :france-price="francePrice" />

      <GamePlayersHistory :appid="game.appid" :name="game.name" heading="Joueurs connectés" has-zoom />

      <GameDna :appid="game.appid" :name="game.name" />

      <SimilarGames :appid="game.appid" />

      <GamePriceHistory v-if="!game.is_free" :appid="game.appid" :name="game.name" />

      <DataBlock
        v-if="!game.is_free"
        title="Le prix dans le monde"
        note="Boutique Steam, dernier relevé, converti en euros au taux de la BCE."
        :is-loading="pricesLoading"
        :has-error="pricesError"
        :is-empty="!worldValues.length"
        empty-message="Pas encore de prix relevé pour ce jeu."
        :height="420"
        @retry="refreshPrices()"
      >
        <template #actions>
          <NuxtLink :to="`/pricing?appid=${game.appid}`" class="link">Tous les pays</NuxtLink>
        </template>
        <WorldValueMap :values="worldValues" :label="`Carte des prix de ${game.name} par pays`" />
      </DataBlock>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { GameDetail } from '~/types'

const FRANCE_ISO3 = 'FRA'

const route = useRoute()
const appid = computed(() => Number(route.params.appid))

const { data: game, hasError, refresh } = useApiResource<GameDetail>(() => `/games/${appid.value}/`)
const {
  prices,
  isLoading: pricesLoading,
  hasError: pricesError,
  refresh: refreshPrices
} = useGamePriceMap(appid)

useHead({ title: () => game.value?.name ?? 'Fiche jeu' })

const francePrice = computed(() => prices.value.find((price) => price.iso3 === FRANCE_ISO3))
const worldValues = computed(() => prices.value.map((price) => ({ iso3: price.iso3, value: price.price_eur })))
const subtitle = computed(() => {
  const current = game.value
  if (!current) return ''
  const studio = current.developers.join(', ')
  return [current.genres.join(' · '), studio && `par ${studio}`].filter(Boolean).join(' — ')
})
</script>
