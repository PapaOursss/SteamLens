<template>
  <div class="ranking">
    <h2 class="title">Classement — Prix les plus bas</h2>
    <p v-if="!rows.length" class="empty">Aucune donnée disponible.</p>
    <table v-else class="table">
      <thead>
        <tr>
          <th class="rank-col">#</th>
          <th>Pays</th>
          <th class="price-col">Prix (€)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in rows" :key="row.iso3" :class="{ highlight: index === 0 }">
          <td class="rank-col">{{ index + 1 }}</td>
          <td>{{ row.name }}</td>
          <td class="price-col">{{ row.price_eur.toFixed(2) }} €</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { CountryPrice } from '~/composables/useGamePriceMap'

const props = defineProps<{
  prices: CountryPrice[]
  countryNames: Record<string, string>
}>()

interface RankRow {
  iso3: string
  name: string
  price_eur: number
}

const rows = computed<RankRow[]>(() =>
  [...props.prices]
    .filter((p) => p.price_eur > 0)
    .sort((a, b) => a.price_eur - b.price_eur)
    .slice(0, 15)
    .map((p) => ({
      iso3: p.iso3,
      name: props.countryNames[p.iso3] ?? p.iso3,
      price_eur: p.price_eur,
    }))
)
</script>

<style scoped>
.ranking { background: #fff; border: 1px solid #e5e7eb; border-radius: 0.75rem; padding: 1.25rem; }
.title { font-size: 1rem; font-weight: 700; margin: 0 0 0.75rem; color: #111827; }
.empty { color: #6b7280; font-size: 0.9rem; }
.table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.table th { text-align: left; padding: 0.4rem 0.5rem; color: #6b7280; border-bottom: 1px solid #e5e7eb; }
.table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #f3f4f6; }
.rank-col { width: 2.5rem; text-align: center; }
.price-col { text-align: right; font-weight: 600; }
.highlight td { background: #ecfdf5; color: #065f46; }
</style>
