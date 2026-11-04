<template>
  <div class="game-selector">
    <label class="label" for="game-search">Sélectionner un jeu</label>
    <input
      id="game-search"
      v-model="query"
      type="search"
      class="input"
      placeholder="Rechercher un jeu Steam…"
      autocomplete="off"
      @focus="open = true"
      @blur="onBlur"
    />
    <ul v-if="open && options.length" class="dropdown">
      <li
        v-for="game in options"
        :key="game.appid"
        class="dropdown-item"
        @mousedown.prevent="select(game)"
      >
        {{ game.name }}
      </li>
    </ul>
    <p v-if="loading" class="hint">Recherche…</p>
  </div>
</template>

<script setup lang="ts">
import type { GameOption } from '~/composables/useGameSearch'

const emit = defineEmits<{ (e: 'select', game: GameOption): void }>()

const query = ref('')
const open = ref(false)
const { options, loading } = useGameSearch(query)

function select(game: GameOption) {
  query.value = game.name
  open.value = false
  emit('select', game)
}

function onBlur() {
  setTimeout(() => { open.value = false }, 150)
}
</script>

<style scoped>
.game-selector { position: relative; width: 100%; max-width: 400px; }
.label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: #374151; }
.input {
  width: 100%; padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db; border-radius: 0.5rem;
  font-size: 0.95rem; outline: none; box-sizing: border-box;
}
.input:focus { border-color: #6366f1; box-shadow: 0 0 0 2px #e0e7ff; }
.dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 10;
  background: #fff; border: 1px solid #e5e7eb; border-radius: 0.5rem;
  margin-top: 0.25rem; list-style: none; padding: 0.25rem 0; max-height: 220px;
  overflow-y: auto; box-shadow: 0 4px 12px rgba(0,0,0,.1);
}
.dropdown-item { padding: 0.5rem 0.75rem; cursor: pointer; font-size: 0.9rem; }
.dropdown-item:hover { background: #f3f4f6; }
.hint { margin-top: 0.3rem; font-size: 0.8rem; color: #6b7280; }
</style>
