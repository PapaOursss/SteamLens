<template>
  <ul :aria-label="label" class="flex min-h-48 flex-wrap content-center items-baseline justify-center gap-x-4 gap-y-1 bg-deep p-6">
    <li
      v-for="word in placedWords"
      :key="word.word"
      class="font-display font-extrabold leading-tight"
      :style="{ fontSize: `${word.size}px`, color, opacity: word.opacity }"
      :title="`${word.word} : dans ${formatNumber(word.count)} avis`"
    >
      {{ word.word }}<span class="sr-only"> ({{ formatNumber(word.count) }} avis)</span>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { ReviewWord } from '~/types'

const MIN_FONT_SIZE = 14
const MAX_FONT_SIZE = 52
const MIN_OPACITY = 0.6

const props = defineProps<{ words: ReviewWord[]; color: string; label: string }>()

/**
 * Taille selon la racine carrée de la fréquence (l'aire du mot suit le nombre d'avis), puis
 * mots rangés par ordre alphabétique pour mêler les grands et les petits.
 */
const placedWords = computed(() => {
  const highest = Math.max(1, ...props.words.map((word) => word.count))
  return props.words
    .map((word) => {
      const weight = Math.sqrt(word.count / highest)
      return {
        ...word,
        size: Math.round(MIN_FONT_SIZE + weight * (MAX_FONT_SIZE - MIN_FONT_SIZE)),
        opacity: MIN_OPACITY + weight * (1 - MIN_OPACITY)
      }
    })
    .sort((first, second) => first.word.localeCompare(second.word, 'fr'))
})
</script>
