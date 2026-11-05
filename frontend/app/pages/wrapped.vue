<template>
  <div>
    <PageIntro :title="data ? `L'année ${data.year} sur Steam` : 'Steam Wrapped'" is-lab>
      Quelques records de l'année. Les cases marquées « exemple » ne sont pas encore calculées.
    </PageIntro>

    <div v-if="isLoading" class="aspect-[2/1] animate-pulse bg-deep motion-reduce:animate-none" />
    <div v-else-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Ces données n'arrivent pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="refresh()">Réessayer</button>
    </div>
    <div v-else-if="data" class="grid gap-px md:grid-cols-2 lg:grid-cols-3">
      <NuxtLink :to="gameLink(data.game_of_the_year.appid)" class="group relative block min-h-72 overflow-hidden bg-deep focus-visible:z-10 focus-visible:-outline-offset-4 md:col-span-2 lg:row-span-2">
        <GameCover
          :sources="heroSources"
          :name="data.game_of_the_year.name"
          :width="1200"
          :height="800"
          is-priority
          class="absolute inset-0 h-full w-full"
        />
        <GameChip :name="data.game_of_the_year.name">
          Le jeu de l'année : pic à <span class="figure">{{ formatNumber(data.game_of_the_year.peak_players) }}</span> joueurs
        </GameChip>
      </NuxtLink>
      <WrappedTile
        label="La plus forte remise"
        :figure="`−${data.biggest_discount.discount_percent} %`"
        :title="data.biggest_discount.name"
        :text="`À ${formatPrice(data.biggest_discount.final_price_eur)} au plus bas.`"
      />
      <WrappedTile
        label="Le genre qui monte"
        :figure="`+${data.trending_genre.growth_percent} %`"
        :title="data.trending_genre.name"
        :text="`Porté par ${data.trending_genre.flagship_game}.`"
        is-sample
      />
      <WrappedTile label="Le flop" :title="data.biggest_flop.name" :text="data.biggest_flop.reason" is-sample />
      <WrappedTile
        class="lg:col-span-2"
        label="Le pays le plus cher"
        :figure="`+${formatNumber(data.most_expensive_country.premium_percent)} %`"
        :title="data.most_expensive_country.country"
        :text="data.most_expensive_country.reason"
        is-sample
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { WrappedStats } from '~/types'

useHead({ title: 'Steam Wrapped' })

const { data, isLoading, hasError, refresh } = useApiResource<WrappedStats>('/stats/wrapped/')

const heroSources = computed(() => {
  const game = data.value?.game_of_the_year
  return game ? heroCoverSources(game.appid, game.header_image) : []
})
</script>
