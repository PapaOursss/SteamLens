<template>
  <div>
    <PageIntro :title="game?.name ?? 'Prix d\'un jeu'">
      <template #under-title>
        <GameSearch field-id="recherche-prix" label="Un autre jeu" class="mt-5 max-w-md" @select="onSelect" />
      </template>
      <GameCover
        v-if="game"
        :key="game.appid"
        :sources="wideCoverSources(game.appid, game.header_image)"
        :name="game.name"
        :width="460"
        :height="215"
        is-priority
        class="aspect-[460/215] h-auto w-full max-w-md"
      />
    </PageIntro>

    <DataBlock
      title="Prix par pays"
      note="Boutique Steam, dernier relevé, converti en euros au taux de la BCE."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!values.length"
      :empty-message="emptyMessage"
      :height="520"
      @retry="refresh()"
    >
      <WorldValueMap :values="values" :label="`Carte des prix de ${game?.name ?? 'ce jeu'} par pays`" />
      <div class="mt-8">
        <CountryPriceLists :values="values" />
      </div>
    </DataBlock>

    <DataBlock v-if="history.length >= MINIMUM_HISTORY" title="Le prix en France, relevé après relevé">
      <TimeLineChart
        :points="history"
        :height="280"
        :label="`Prix de ${game?.name ?? 'ce jeu'} en France au fil du temps`"
        :format-value="formatPrice"
        :format-axis="formatPrice"
      />
    </DataBlock>

    <GamePlayersHistory v-if="game" :appid="game.appid" :name="game.name" />
  </div>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'
import type { GameDetail } from '~/types'

/** Jeu affiché sans choix : payant, suivi, et dont les prix sont relevés. */
const DEFAULT_APPID = 1091500
const MINIMUM_HISTORY = 2
const HISTORY_COUNTRY = 'FR'

const route = useRoute()
const appid = computed(() => Number(route.query.appid) || DEFAULT_APPID)

const { data: game } = useApiResource<GameDetail>(() => `/games/${appid.value}/`)
const { prices, points, isLoading, hasError, refresh } = useGamePriceMap(appid)

useHead({ title: () => (game.value ? `Prix de ${game.value.name}` : 'Prix') })

const values = computed(() => prices.value.map((price) => ({ iso3: price.iso3, value: price.price_eur })))
const history = computed(() =>
  points.value
    .filter((point) => point.country === HISTORY_COUNTRY && point.price_eur !== null)
    .map((point) => ({ date: point.date, value: Number(point.price_eur) }))
)
const emptyMessage = computed(() =>
  game.value?.is_free ? 'Ce jeu est gratuit : aucun prix à comparer.' : 'Pas encore de prix relevé pour ce jeu.'
)

function onSelect(selected: GameOption) {
  navigateTo({ query: { appid: selected.appid } })
}
</script>
