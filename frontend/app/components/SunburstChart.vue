<template>
  <div class="sunburst-container">
    <div class="breadcrumbs">
      <span class="crumb root" @click="selectedNode = null">Tout IGDB</span>
      <template v-if="selectedNode">
        <span class="separator">/</span>
        <span class="crumb active">{{ selectedNode.name }}</span>
      </template>
    </div>

    <div class="sunburst-rings">
      <!-- Anneau Genres -->
      <div class="ring genres-ring">
        <h4 class="ring-title">Genres (Niveau 1)</h4>
        <div class="chips-list">
          <button
            v-for="genre in data"
            :key="genre.name"
            class="chip chip-genre"
            :class="{ active: selectedGenre?.name === genre.name }"
            @click="selectGenre(genre)"
          >
            {{ genre.name }}
            <span class="chip-count">{{ genre.value }} jeux</span>
          </button>
        </div>
      </div>

      <!-- Anneau Thèmes -->
      <div v-if="selectedGenre" class="ring themes-ring">
        <h4 class="ring-title">Thèmes associés (Niveau 2)</h4>
        <div class="chips-list">
          <button
            v-for="theme in selectedGenre.children"
            :key="theme.name"
            class="chip chip-theme"
            :class="{ active: selectedTheme?.name === theme.name }"
            @click="selectTheme(theme)"
          >
            {{ theme.name }}
            <span class="chip-count">{{ theme.value }}</span>
          </button>
        </div>
      </div>

      <!-- Anneau Modes de jeu -->
      <div v-if="selectedTheme" class="ring modes-ring">
        <h4 class="ring-title">Modes de jeu (Niveau 3)</h4>
        <div class="chips-list">
          <div
            v-for="mode in selectedTheme.children"
            :key="mode.name"
            class="chip chip-mode"
          >
            {{ mode.name }}
            <span class="chip-count">{{ mode.value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export interface SunburstMode {
  name: string
  value: number
}

export interface SunburstTheme {
  name: string
  value: number
  children?: SunburstMode[]
}

export interface SunburstGenre {
  name: string
  value: number
  children?: SunburstTheme[]
}

const props = defineProps<{
  data: SunburstGenre[]
}>()

const selectedGenre = ref<SunburstGenre | null>(props.data[0] || null)
const selectedTheme = ref<SunburstTheme | null>(props.data[0]?.children?.[0] || null)
const selectedNode = ref<SunburstGenre | SunburstTheme | null>(null)

function selectGenre(genre: SunburstGenre) {
  selectedGenre.value = genre
  selectedTheme.value = genre.children?.[0] || null
  selectedNode.value = genre
}

function selectTheme(theme: SunburstTheme) {
  selectedTheme.value = theme
  selectedNode.value = theme
}
</script>

<style scoped>
.sunburst-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #4b5563;
}

.crumb {
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
}

.crumb.root:hover {
  background: #f3f4f6;
  color: #111827;
}

.crumb.active {
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
}

.separator {
  color: #9ca3af;
}

.sunburst-rings {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.ring {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
}

.ring-title {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6b7280;
  margin: 0 0 0.75rem 0;
  font-weight: 700;
}

.chips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease-in-out;
}

.chip-genre {
  background: #e0e7ff;
  color: #3730a3;
}

.chip-genre:hover, .chip-genre.active {
  background: #4f46e5;
  color: #ffffff;
}

.chip-theme {
  background: #fef3c7;
  color: #92400e;
}

.chip-theme:hover, .chip-theme.active {
  background: #d97706;
  color: #ffffff;
}

.chip-mode {
  background: #dcfce7;
  color: #166534;
  cursor: default;
}

.chip-count {
  font-size: 0.75rem;
  opacity: 0.85;
  padding: 0.1rem 0.35rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.08);
}
</style>
