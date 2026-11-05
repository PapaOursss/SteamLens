<template>
  <div>
    <div class="grid gap-8 md:grid-cols-2">
      <div>
        <h3 class="mb-3 text-xl">Les moins chers</h3>
        <RankBars :rows="cheapest" :maximum="highest" />
      </div>
      <div>
        <h3 class="mb-3 text-xl">Les plus chers</h3>
        <RankBars :rows="dearest" :maximum="highest" />
      </div>
    </div>

    <details class="mt-6">
      <summary class="link cursor-pointer">Tous les pays ({{ sorted.length }})</summary>
      <div class="overflow-x-auto">
        <table class="data-table mt-2 max-w-xl">
          <thead>
            <tr>
              <th scope="col">Pays</th>
              <th scope="col">Prix</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sorted" :key="row.key">
              <td>{{ row.label }}</td>
              <td class="figure">{{ row.display }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import type { CountryValue, RankRow } from '~/types'

const LIST_LENGTH = 8

const props = defineProps<{ values: CountryValue[] }>()

const sorted = computed<RankRow[]>(() =>
  [...props.values]
    .sort((first, second) => first.value - second.value)
    .map((entry) => ({
      key: entry.iso3,
      label: countryName(entry.iso3),
      value: entry.value,
      display: formatPrice(entry.value)
    }))
)

const highest = computed(() => sorted.value[sorted.value.length - 1]?.value ?? 1)
const cheapest = computed(() => sorted.value.slice(0, LIST_LENGTH))
const dearest = computed(() => sorted.value.slice(-LIST_LENGTH).reverse())
</script>
