<template>
  <DataBlock
    title="Le prix et ses promos"
    note="Prix sur Steam en France, et prix hors promo. Source : IsThereAnyDeal."
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!history?.changes.length"
    empty-message="Pas encore d'historique de prix pour ce jeu."
    :height="320"
    @retry="refresh()"
  >
    <PriceStepChart
      v-if="history"
      :changes="history.changes"
      :currency="history.currency"
      :label="`Prix de ${name} au fil du temps`"
    />
  </DataBlock>
</template>

<script setup lang="ts">
import type { PriceHistory } from '~/types'

const props = defineProps<{ appid: number; name: string }>()

const { data: history, isLoading, hasError, refresh } = useApiResource<PriceHistory>(
  () => `/stats/price-history/${props.appid}/`
)
</script>
