<template>
  <div>
    <PageIntro
      title="Bonnes affaires du moment"
      tagline="Les plus grosses remises du jour sur les jeux PC les mieux notés (Steam, GOG, Humble, Fanatical… source CheapShark)."
    />

    <DataBlock
      title="Offres immanquables"
      note="Offres triées par Deal Rating, sur les jeux ayant au moins 70% d'avis positifs sur Steam."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!deals || !deals.length"
      empty-message="Aucune promotion trouvée pour le moment."
      @retry="refresh()"
    >
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="deal in deals"
          :key="deal.deal_id"
          class="flex flex-col justify-between overflow-hidden rounded-lg border border-line bg-raised transition hover:border-hot"
        >
          <div class="p-4">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-bold text-text leading-snug line-clamp-2">
                {{ deal.title }}
              </h3>
              <span class="rounded bg-hot px-2 py-0.5 text-xs font-extrabold text-deep shrink-0">
                -{{ deal.cut_percent }}%
              </span>
            </div>

            <div class="mt-2 flex items-center gap-2 text-xs text-soft">
              <img v-if="deal.store_icon" :src="deal.store_icon" :alt="deal.store_name" class="h-4 w-4" />
              <span>{{ deal.store_name }}</span>
              <span v-if="deal.steam_rating_percent" class="ml-auto text-hot font-semibold">
                ★ {{ deal.steam_rating_percent }}% avis positifs
              </span>
            </div>

            <div class="mt-4 flex items-baseline gap-2">
              <span class="font-mono text-xl font-black text-text">
                {{ deal.sale_price.toFixed(2) }} $
              </span>
              <span v-if="deal.normal_price > deal.sale_price" class="font-mono text-sm text-soft line-through">
                {{ deal.normal_price.toFixed(2) }} $
              </span>
            </div>
          </div>

          <div class="flex border-t border-line bg-deep/50 p-2 text-xs">
            <NuxtLink
              v-if="deal.steam_appid"
              :to="`/games/${deal.steam_appid}`"
              class="flex-1 py-1.5 text-center font-medium text-soft hover:text-text"
            >
              Fiche jeu
            </NuxtLink>
            <a
              :href="deal.redirect_url"
              target="_blank"
              rel="noopener noreferrer"
              class="flex-1 rounded bg-hot/10 py-1.5 text-center font-bold text-hot transition hover:bg-hot hover:text-deep"
            >
              Voir l'offre ↗
            </a>
          </div>
        </article>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
export interface DealItem {
  title: string
  deal_id: string
  store_name: string
  store_icon: string
  sale_price: number
  normal_price: number
  cut_percent: number
  steam_rating_percent: number
  steam_rating_text: string
  deal_rating: number
  steam_appid: number | null
  thumb: string
  redirect_url: string
}

useHead({ title: 'Bonnes affaires — SteamLens' })

const { data: deals, isLoading, hasError, refresh } = useApiResource<DealItem[]>(() => '/stats/deals/')
</script>
