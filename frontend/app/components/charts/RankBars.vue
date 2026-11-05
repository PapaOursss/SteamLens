<template>
  <ol class="space-y-2">
    <li v-for="row in rows" :key="row.key">
      <component :is="row.to ? NuxtLink : 'div'" :to="row.to" class="block" :class="{ 'hover:text-hot': row.to }">
        <span class="flex justify-between gap-4">
          <span>{{ row.label }}</span>
          <span class="figure shrink-0">{{ row.display }}</span>
        </span>
        <span class="mt-1 block h-3 rounded-r bg-soft" :style="{ width: `${widthOf(row)}%` }" aria-hidden="true" />
      </component>
    </li>
  </ol>
</template>

<script setup lang="ts">
import { NuxtLink } from '#components'
import type { RankRow } from '~/types'

const PERCENT = 100
const SMALLEST_WIDTH = 1

/** `maximum` : pour comparer plusieurs listes à la même échelle. */
const props = defineProps<{ rows: RankRow[]; maximum?: number }>()

const largest = computed(() => props.maximum ?? Math.max(...props.rows.map((row) => row.value), 1))

function widthOf(row: RankRow): number {
  return Math.max((row.value / largest.value) * PERCENT, SMALLEST_WIDTH)
}
</script>
