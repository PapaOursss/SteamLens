<template>
  <DataBlock
    :title="title"
    note="Prix moyen en euros, au dernier relevé de la boutique Steam."
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!values.length"
    empty-message="Pas encore de prix relevés."
    :height="480"
    @retry="refresh()"
  >
    <template #actions>
      <NuxtLink to="/world" class="link">Toute la carte</NuxtLink>
    </template>
    <WorldValueMap :values="values" label="Carte du prix moyen d'un jeu par pays" />
  </DataBlock>
</template>

<script setup lang="ts">
import type { WorldMapData } from '~/types'

const { data, isLoading, hasError, refresh } = useApiResource<WorldMapData>('/map/average-price-eur/')

const values = computed(() =>
  Object.entries(data.value ?? {}).map(([iso3, value]) => ({ iso3, value }))
)

const title = computed(() => {
  if (!values.value.length) return 'À quel prix, selon le pays'
  const sorted = [...values.value].sort((first, second) => first.value - second.value)
  const cheapest = sorted[0]!
  const dearest = sorted[sorted.length - 1]!
  return `Un jeu coûte ${formatPrice(cheapest.value)} (${countryName(cheapest.iso3)}) ou ${formatPrice(dearest.value)} (${countryName(dearest.iso3)})`
})
</script>
