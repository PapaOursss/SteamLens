<template>
  <div>
    <PageIntro title="Bonnes affaires du moment">
      Les plus grosses remises du jour sur des jeux PC bien notés, d'une boutique à l'autre (Steam,
      GOG, Humble, Fanatical…). Une offre par jeu, la mieux classée.
    </PageIntro>

    <DataBlock
      title="Offres immanquables"
      note="Classées par CheapShark (remise, note et prix), sur les jeux à 70 % d'avis positifs ou plus sur Steam. Prix en dollars US."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!deals?.length"
      empty-message="Aucune promotion trouvée pour le moment."
      @retry="refresh()"
    >
      <ul class="grid gap-px sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
        <li v-for="deal in deals" :key="deal.deal_id" class="flex flex-col bg-deep">
          <div class="relative aspect-[460/215] overflow-hidden bg-raised">
            <GameCover
              :sources="coverSources(deal)"
              :name="deal.title"
              :width="460"
              :height="215"
              class="h-full w-full"
            />
            <span class="figure absolute right-0 top-0 bg-hot px-2 py-1 font-display text-lg font-extrabold text-deep">
              −{{ deal.cut_percent }} %
            </span>
          </div>

          <div class="flex flex-1 flex-col gap-2 p-4">
            <h3 class="line-clamp-2 text-xl leading-tight">{{ deal.title }}</h3>
            <p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-soft">
              <span class="inline-flex items-center gap-2">
                <img v-if="deal.store_icon" :src="deal.store_icon" alt="" width="16" height="16" class="h-4 w-4">
                {{ deal.store_name }}
              </span>
              <span v-if="deal.steam_rating_percent">{{ formatPercent(deal.steam_rating_percent) }} d'avis positifs</span>
            </p>
            <p class="figure mt-auto flex items-baseline gap-3 pt-2">
              <strong class="font-display text-3xl font-extrabold">{{ usd(deal.sale_price) }}</strong>
              <s v-if="deal.normal_price > deal.sale_price" class="text-soft">{{ usd(deal.normal_price) }}</s>
            </p>
            <div class="flex flex-wrap items-center gap-x-4 gap-y-2 pt-2">
              <a :href="deal.redirect_url" target="_blank" rel="noopener noreferrer" class="button">
                Voir l'offre<span class="sr-only"> (nouvel onglet)</span>
              </a>
              <NuxtLink v-if="deal.steam_appid" :to="gameLink(deal.steam_appid)" class="link">Fiche du jeu</NuxtLink>
            </div>
          </div>
        </li>
      </ul>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { TopDeal } from '~/types'

useHead({ title: 'Bonnes affaires' })

const { data: deals, isLoading, hasError, refresh } = useApiResource<TopDeal[]>('/stats/deals/')

function usd(value: number): string {
  return formatAmount(value, 'USD')
}

/** L'image Steam du jeu quand on la connaît, sinon la vignette (petite) de CheapShark. */
function coverSources(deal: TopDeal): string[] {
  const thumb = deal.thumb ? [deal.thumb] : []
  return deal.steam_appid ? [...wideCoverSources(deal.steam_appid), ...thumb] : thumb
}
</script>
