<template>
  <div>
    <ul class="mb-4 flex flex-wrap gap-x-5 gap-y-2" aria-label="Légende : niveaux ProtonDB">
      <li v-for="tier in TIERS" :key="tier.key" class="flex items-center gap-2">
        <span class="h-3 w-6 rounded-sm" :style="{ backgroundColor: tier.fill }" aria-hidden="true" />
        {{ tier.label }}
      </li>
    </ul>

    <ul class="space-y-3">
      <li v-for="row in rows" :key="row.genre">
        <p class="flex justify-between gap-4">
          <span>{{ row.genre }}</span>
          <span class="figure text-soft">{{ formatNumber(row.total) }} jeux</span>
        </p>
        <div class="mt-1 flex h-4 gap-0.5" aria-hidden="true">
          <span
            v-for="tier in TIERS"
            :key="tier.key"
            :style="{ width: `${(row.counts[tier.key] / row.total) * 100}%`, backgroundColor: tier.fill }"
            :title="`${tier.label} : ${row.counts[tier.key]}`"
          />
        </div>
      </li>
    </ul>

    <details class="mt-6">
      <summary class="link cursor-pointer">Le détail en tableau</summary>
      <div class="overflow-x-auto">
        <table class="data-table mt-2">
          <thead>
            <tr>
              <th scope="col">Genre</th>
              <th v-for="tier in TIERS" :key="tier.key" scope="col">{{ tier.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.genre">
              <td>{{ row.genre }}</td>
              <td v-for="tier in TIERS" :key="tier.key" class="figure">{{ row.counts[tier.key] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import type { TierCounts } from '~/types'

const TIERS: { key: keyof TierCounts; label: string; fill: string }[] = [
  { key: 'platinum', label: 'Platine', fill: SEQUENTIAL_COLORS[4] },
  { key: 'gold', label: 'Or', fill: SEQUENTIAL_COLORS[3] },
  { key: 'silver', label: 'Argent', fill: SEQUENTIAL_COLORS[2] },
  { key: 'bronze', label: 'Bronze', fill: SEQUENTIAL_COLORS[1] },
  { key: 'borked', label: 'Injouable', fill: COLORS.hot }
]

const props = defineProps<{ genres: { genre: string; counts: TierCounts }[] }>()

const rows = computed(() =>
  props.genres
    .map((row) => ({
      ...row,
      total: Object.values(row.counts).reduce((sum, count) => sum + count, 0)
    }))
    .filter((row) => row.total > 0)
)
</script>
