<template>
  <DataBlock v-if="data?.length" title="Gratuit en ce moment" note="Jeux Steam offerts. Source : GamerPower.">
    <ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <li v-for="offer in data.slice(0, MAX_OFFERS)" :key="offer.id">
        <a :href="offer.url" target="_blank" rel="noopener noreferrer" class="block h-full bg-deep hover:text-hot">
          <img v-if="offer.image" :src="offer.image" alt="" loading="lazy" class="aspect-[460/215] w-full object-cover">
          <span class="block p-3">
            <span class="block font-semibold">{{ offer.title }}</span>
            <span class="text-sm text-soft">{{ endLabel(offer) }}</span>
          </span>
        </a>
      </li>
    </ul>
  </DataBlock>
</template>

<script setup lang="ts">
import type { Giveaway } from '~/types'

const MAX_OFFERS = 8

/** Sans offre ou source en panne, l'encart disparaît : l'accueil n'en dépend pas. */
const { data } = useApiResource<Giveaway[]>('/stats/giveaways/')

function endLabel(offer: Giveaway): string {
  return offer.end_date ? `Jusqu'au ${formatDate(offer.end_date.slice(0, 10))}` : 'Sans date de fin annoncée'
}
</script>
