<template>
  <div class="relative">
    <label class="flex min-h-11 items-center gap-2 rounded-md bg-deep px-3 focus-within:outline focus-within:outline-[3px] focus-within:outline-offset-2 focus-within:outline-hot">
      <span class="shrink-0 text-soft">{{ label }}</span>
      <input
        :id="fieldId"
        v-model="query"
        type="search"
        role="combobox"
        autocomplete="off"
        class="min-w-0 flex-1 bg-transparent py-2 text-text outline-none [&::-webkit-search-cancel-button]:hidden"
        aria-autocomplete="list"
        :aria-expanded="isOpen"
        :aria-controls="`${fieldId}-resultats`"
        :aria-activedescendant="activeIndex >= 0 ? `${fieldId}-${activeIndex}` : undefined"
        @focus="hasFocus = true"
        @blur="hasFocus = false"
        @keydown="onKeydown"
      >
    </label>

    <ul
      v-show="isOpen"
      :id="`${fieldId}-resultats`"
      role="listbox"
      :aria-label="label"
      class="absolute right-0 top-full z-40 mt-1 max-h-96 w-full min-w-72 overflow-y-auto rounded-md border border-line bg-deep"
    >
      <li
        v-for="(game, index) in options"
        :id="`${fieldId}-${index}`"
        :key="game.appid"
        role="option"
        :aria-selected="index === activeIndex"
        class="flex min-h-11 cursor-pointer items-center gap-3 p-2"
        :class="index === activeIndex ? 'bg-raised' : 'hover:bg-raised'"
        @mousedown.prevent="choose(game)"
      >
        <GameCover
          :sources="wideCoverSources(game.appid, game.header_image)"
          :name="game.name"
          :width="64"
          :height="30"
          class="h-[30px] w-16 shrink-0"
        />
        <span>{{ game.name }}</span>
      </li>
      <li v-if="message" class="p-3 text-soft">{{ message }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'

const MINIMUM_QUERY_LENGTH = 2

const props = withDefaults(defineProps<{ fieldId: string; label?: string; keepChoice?: boolean }>(), {
  label: 'Chercher un jeu',
  keepChoice: false
})
const emit = defineEmits<{ select: [game: GameOption] }>()

const query = ref('')
const hasFocus = ref(false)
const activeIndex = ref(-1)
const { options, isLoading, hasError } = useGameSearch(query)

const canSearch = computed(() => query.value.trim().length >= MINIMUM_QUERY_LENGTH)
const isOpen = computed(() => hasFocus.value && canSearch.value)
const message = computed(() => {
  if (options.value.length) return ''
  if (isLoading.value) return 'Recherche…'
  return hasError.value ? "La recherche ne répond pas pour l'instant." : 'Aucun jeu à ce nom.'
})

watch(options, () => {
  activeIndex.value = -1
})

function choose(game: GameOption) {
  query.value = props.keepChoice ? game.name : ''
  hasFocus.value = false
  emit('select', game)
}

function moveActive(step: number) {
  if (!options.value.length) return
  const count = options.value.length
  activeIndex.value = (activeIndex.value + step + count) % count
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowDown') moveActive(1)
  else if (event.key === 'ArrowUp') moveActive(-1)
  else if (event.key === 'Escape') hasFocus.value = false
  else if (event.key === 'Enter' && options.value.length && !isLoading.value) {
    choose(options.value[Math.max(activeIndex.value, 0)]!)
  } else return
  event.preventDefault()
}
</script>
