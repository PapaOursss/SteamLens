<template>
  <span class="absolute bottom-0 left-0 max-w-full bg-deep px-2 py-1 text-xs leading-snug text-soft group-hover:bg-hot group-hover:text-deep sm:text-sm">
    <span class="block font-semibold text-text group-hover:text-deep">{{ name }}</span>
    <slot />
  </span>
</template>

<script setup lang="ts">
defineProps<{ name: string }>()
</script>
