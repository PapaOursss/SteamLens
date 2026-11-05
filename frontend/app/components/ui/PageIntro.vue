<template>
  <div class="gutter grid gap-4 pb-8 pt-8 md:pb-10 md:pt-12 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-end lg:gap-10">
    <div>
      <NuxtLink v-if="isLab" to="/lab" class="link mb-1 text-soft">Labo</NuxtLink>
      <h1 class="text-4xl leading-none sm:text-5xl lg:text-6xl">{{ title }}</h1>
      <slot name="under-title" />
    </div>
    <div class="max-w-prose text-lg leading-relaxed text-soft">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; isLab?: boolean }>()
</script>
