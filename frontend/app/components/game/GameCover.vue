<template>
  <img
    v-if="currentSource"
    :src="currentSource"
    :alt="alt"
    :width="width"
    :height="height"
    :loading="isPriority ? 'eager' : 'lazy'"
    :fetchpriority="isPriority ? 'high' : undefined"
    decoding="async"
    class="block bg-deep object-cover"
    @error="sourceIndex++"
  >
  <div v-else class="flex items-center justify-center overflow-hidden bg-raised p-2 text-center font-display font-bold text-soft" aria-hidden="true">
    {{ initial }}
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    sources: string[]
    name: string
    width: number
    height: number
    alt?: string
    isPriority?: boolean
  }>(),
  { alt: '', isPriority: false }
)

const sourceIndex = ref(0)
const currentSource = computed(() => props.sources[sourceIndex.value])
const initial = computed(() => props.name.charAt(0).toUpperCase())

watch(
  () => props.sources.join(),
  () => {
    sourceIndex.value = 0
  }
)
</script>
