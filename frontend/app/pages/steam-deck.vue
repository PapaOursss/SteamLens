<template>
  <div>
    <PageIntro title="Ce qui tourne sous Linux" is-lab>
      La compatibilité des jeux avec Proton, donc avec le Steam Deck, d'après les rapports de ProtonDB.
    </PageIntro>

    <DataBlock
      title="Les niveaux, genre par genre"
      note="ProtonDB. Platine : marche sans réglage. Injouable : ne marche pas."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!hasReports"
      empty-message="Pas encore de données : l'import ProtonDB n'a pas tourné sur cette base."
      :height="420"
      @retry="refresh()"
    >
      <ProtonStacks :genres="data!.by_genre" />
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { ProtonStats } from '~/types'

useHead({ title: 'Steam Deck' })

const { data, isLoading, hasError, refresh } = useApiResource<ProtonStats>('/stats/proton/')

const hasReports = computed(() =>
  (data.value?.by_genre ?? []).some((row) => Object.values(row.counts).some((count) => count > 0))
)
</script>
