<template>
  <section class="gutter py-8 md:py-10">
    <h2 class="mb-4 text-2xl md:text-3xl">La pépite du jour</h2>
    <div class="flex flex-wrap items-center gap-6">
      <GameTile class="w-full sm:w-96" :appid="gem.appid" :name="gem.name" :header-image="gem.header_image" />
      <div class="max-w-prose">
        <p v-if="gem.short_description" class="mb-2 leading-relaxed text-soft">{{ gem.short_description }}</p>
        <p class="figure text-xl font-semibold">{{ gem.price_eur > 0 ? formatPrice(gem.price_eur) : 'Gratuit' }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { DashboardGem } from '~/types'

defineProps<{ gem: DashboardGem }>()
</script>
