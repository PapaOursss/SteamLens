<template>
  <article class="flex min-h-64 flex-col justify-end gap-2 bg-deep p-5 md:p-6">
    <p class="text-soft">
      {{ label }}
      <span v-if="isSample" class="ml-1 rounded-sm bg-hot px-1.5 py-0.5 text-sm font-semibold text-deep">exemple</span>
    </p>
    <p v-if="figure" class="figure font-display text-5xl font-extrabold md:text-6xl">{{ figure }}</p>
    <h2 class="text-2xl leading-tight">{{ title }}</h2>
    <p v-if="text" class="max-w-prose leading-relaxed text-soft">{{ text }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{ label: string; title: string; figure?: string; text?: string; isSample?: boolean }>()
</script>
