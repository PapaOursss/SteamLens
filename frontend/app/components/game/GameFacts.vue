<template>
  <div class="gutter mb-10 grid grid-cols-2 gap-x-8 gap-y-4 lg:grid-cols-4">
    <StatTile label="Prix en France" :value="price" :hint="discount" />
    <StatTile label="Avis positifs" :value="game.positive_share === null ? '—' : formatPercent(game.positive_share)" hint="Steam, toutes langues" />
    <StatTile label="Metacritic" :value="game.metacritic_score ?? '—'" />
    <StatTile label="Sortie" :value="game.release_date ? formatDate(game.release_date) : '—'" />
  </div>
</template>

<script setup lang="ts">
import type { CountryPrice } from '~/composables/useGamePriceMap'
import type { GameDetail } from '~/types'

const props = defineProps<{ game: GameDetail; francePrice: CountryPrice | undefined }>()

const price = computed(() => {
  if (props.game.is_free) return 'Gratuit'
  return props.francePrice ? formatPrice(props.francePrice.price_eur) : '—'
})
const discount = computed(() => {
  const percent = props.francePrice?.discount_percent
  return percent ? `En promo : −${formatPercent(percent)}` : undefined
})
</script>
