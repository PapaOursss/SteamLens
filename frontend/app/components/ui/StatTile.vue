<template>
  <div>
    <p class="text-soft">{{ label }}</p>
    <p class="figure font-display text-3xl font-extrabold tracking-tight">{{ value }}</p>
    <p v-if="hint" class="text-soft">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string | number; hint?: string }>()
</script>
