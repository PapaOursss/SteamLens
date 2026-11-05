<template>
  <div>
    <PageIntro title="Un même catalogue, des prix différents">
      Le prix moyen d'un jeu dans chaque pays où la boutique Steam a été relevée, converti en euros au taux de la BCE.
    </PageIntro>

    <DataBlock
      title="Prix moyen par pays"
      note="Boutique Steam et taux Frankfurter."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!values.length"
      empty-message="Pas encore de prix relevés."
      :height="620"
      @retry="refresh()"
    >
      <WorldValueMap :values="values" label="Carte du prix moyen d'un jeu par pays" />
      <div class="mt-8">
        <CountryPriceLists :values="values" />
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { WorldMapData } from '~/types'

useHead({ title: 'Monde' })

const { data, isLoading, hasError, refresh } = useApiResource<WorldMapData>('/map/average-price-eur/')

const values = computed(() =>
  Object.entries(data.value ?? {}).map(([iso3, value]) => ({ iso3, value }))
)
</script>
