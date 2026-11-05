<template>
  <ClientOnly>
    <VChart
      class="h-full w-full"
      :style="height ? { height: `${height}px` } : undefined"
      :option="option"
      :init-options="{ locale: 'FR' }"
      role="img"
      :aria-label="label"
      autoresize
    />
    <template #fallback>
      <div class="h-full bg-deep" :style="height ? { height: `${height}px` } : undefined" />
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
/** Sans `height`, le graphique remplit son parent. */
defineProps<{ option: object; height?: number; label: string }>()
</script>
