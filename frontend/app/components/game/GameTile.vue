<template>
  <NuxtLink :to="gameLink(appid)" class="group relative block aspect-[460/215] overflow-hidden bg-deep focus-visible:z-10 focus-visible:-outline-offset-4">
    <GameCover
      :sources="wideCoverSources(appid, headerImage)"
      :name="name"
      :width="460"
      :height="215"
      class="h-full w-full"
    />
    <GameChip :name="name"><slot /></GameChip>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{ appid: number; name: string; headerImage: string }>()
</script>
