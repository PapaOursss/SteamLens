<template>
  <div>
    <PageIntro title="Réseau des tags" is-lab>
      Les tags qui apparaissent ensemble sur les jeux Steam. Les liens indiquent une forte co-occurrence, et les couleurs regroupent les familles de tags.
    </PageIntro>

    <DataBlock
      title="Familles et associations de tags"
      note="Graphe de forces limité aux 150 tags les plus fréquents."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.nodes.length"
      empty-message="Pas encore de données de tags disponibles."
      :height="660"
      @retry="refresh()"
    >
      <TagNetworkChart :nodes="data!.nodes" :edges="data!.edges" :height="620" />
    </DataBlock>

    <p class="gutter max-w-prose text-soft">
      Glissez les nœuds pour explorer les connexions. Les communautés de tags (familles) sont détectées par proximité thématique sur les jeux communs.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { TagNetworkResponse } from '~/types'

useHead({ title: 'Réseau des tags' })

const { data, isLoading, hasError, refresh } = useApiResource<TagNetworkResponse>('/stats/tag-network/')
</script>
