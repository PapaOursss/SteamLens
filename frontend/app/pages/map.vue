<template>
  <div class="page">
    <header class="header">
      <h1 class="title">Prix d'un jeu dans le monde</h1>
      <p class="subtitle">
        Carte choroplèthe des prix Steam par pays, convertis en euros (taux BCE).
      </p>
      <GameSelector class="selector" @select="onGameSelect" />
    </header>

    <div v-if="!selectedAppid" class="empty-state">
      <span class="emoji">🗺️</span>
      <p>Recherchez un jeu pour afficher ses prix sur la carte.</p>
    </div>

    <template v-else>
      <div v-if="loading" class="loading">Chargement des prix…</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <template v-else-if="prices.length">
        <WorldChoropleth :prices="prices" :country-names="countryNames" class="map-section" />
        <PriceRankingTable :prices="prices" :country-names="countryNames" class="ranking-section" />
      </template>
      <div v-else class="empty-state">
        <span class="emoji">📭</span>
        <p>Aucun prix disponible pour ce jeu.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'

const selectedAppid = ref<number | null>(null)
const { prices, loading, error } = useGamePriceMap(selectedAppid)

function onGameSelect(game: GameOption) {
  selectedAppid.value = game.appid
}

/**
 * Table de correspondance iso3 → nom du pays.
 * Chargée depuis le GeoJSON déjà présent dans public/.
 */
const countryNames = ref<Record<string, string>>({})

onMounted(async () => {
  try {
    const geo = await $fetch<{ features: GeoFeature[] }>('/world-110m.json')
    const map: Record<string, string> = {}
    for (const f of geo.features) {
      if (f.properties.iso3 && f.properties.iso3 !== '-99') {
        map[f.properties.iso3] = f.properties.name
      }
    }
    countryNames.value = map
  } catch {
    // La carte reste fonctionnelle sans les noms
  }
})

interface GeoFeature {
  properties: { iso3: string; name: string }
}
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; font-family: system-ui, sans-serif; color: #1f2937; }
.header { margin-bottom: 2rem; }
.title { font-size: 2rem; font-weight: 800; margin: 0 0 0.4rem; }
.subtitle { color: #4b5563; margin: 0 0 1.25rem; }
.selector { margin-top: 0.5rem; }
.map-section { margin-bottom: 1.5rem; }
.ranking-section { margin-bottom: 2rem; }
.loading, .error { padding: 2rem; text-align: center; color: #6b7280; }
.error { color: #dc2626; }
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 4rem 2rem; color: #6b7280;
}
.emoji { font-size: 3rem; }
</style>
