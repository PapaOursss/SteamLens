<template>
  <p class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
    <span class="figure">{{ low }}</span>
    <span class="h-3 w-36 rounded-sm" :style="{ background: GRADIENT }" aria-hidden="true" />
    <span class="figure">{{ high }}</span>
    <span class="ml-3 flex items-center gap-2 text-soft">
      <span class="h-3 w-6 rounded-sm bg-deep" aria-hidden="true" />
      {{ noDataLabel }}
    </span>
  </p>
</template>

<script setup lang="ts">
const GRADIENT = `linear-gradient(to right, ${SEQUENTIAL_COLORS.join(', ')})`

defineProps<{ low: string; high: string; noDataLabel: string }>()
</script>
