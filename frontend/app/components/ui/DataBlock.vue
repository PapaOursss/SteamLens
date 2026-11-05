<template>
  <section class="gutter py-8 md:py-10">
    <div class="mb-4 flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
      <div>
        <h2 class="text-2xl leading-tight md:text-3xl">{{ title }}</h2>
        <p v-if="note" class="mt-1 max-w-prose text-soft">{{ note }}</p>
      </div>
      <slot name="actions" />
    </div>

    <div v-if="isLoading" class="animate-pulse bg-deep motion-reduce:animate-none" :style="{ height: `${height}px` }">
      <span class="sr-only">Chargement</span>
    </div>
    <div v-else-if="hasError" class="flex flex-wrap items-center gap-4 bg-deep p-6" role="alert">
      <p>Ces données n'arrivent pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="$emit('retry')">Réessayer</button>
    </div>
    <p v-else-if="isEmpty" class="bg-deep p-6 text-soft">{{ emptyMessage }}</p>
    <slot v-else />
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    note?: string
    isLoading?: boolean
    hasError?: boolean
    isEmpty?: boolean
    emptyMessage?: string
    height?: number
  }>(),
  { note: undefined, emptyMessage: 'Pas encore de données ici.', height: 240 }
)

defineEmits<{ retry: [] }>()
</script>
