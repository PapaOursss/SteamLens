<template>
  <div>
    <PageIntro title="Du genre au prix, jusqu'à l'accueil" is-lab>
      Les jeux chers sont-ils mieux notés ? Ce diagramme Sankey visualise les flux reliant chaque genre à sa tranche de prix, puis au verdict des joueurs.
    </PageIntro>

    <SampleNotice v-if="data?.is_sample" class="mb-6">
      Les prix et les avis n'ont pas encore été importés : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <DataBlock
      title="Flux Genre → Tranche de prix → Accueil"
      note="Tranches : gratuit, < 5 €, 5-15 €, 15-30 €, > 30 €. Accueil basé sur le pourcentage d'avis positifs."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.nodes.length"
      empty-message="Pas de flux disponibles."
      :height="600"
      @retry="refresh()"
    >
      <SankeyPriceChart :nodes="data!.nodes" :links="data!.links" :height="540" />
    </DataBlock>

    <p class="gutter max-w-prose text-soft">
      Passez votre curseur sur un genre, une tranche de prix ou un accueil pour mettre en valeur les flux associés et suivre la trajectoire des jeux.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { SankeyPriceReviewResponse } from '~/types'

useHead({ title: 'Genre, prix et accueil' })

const { data, isLoading, hasError, refresh } = useApiResource<SankeyPriceReviewResponse>('/stats/sankey-pricing/')
</script>
