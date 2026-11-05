<template>
  <div class="treemap-wrapper">
    <div class="treemap-grid">
      <div
        v-for="genre in sortedGenres"
        :key="genre.id"
        class="genre-block"
        :style="{ flexGrow: getWeight(genre) }"
      >
        <div class="genre-header">
          <span class="genre-title">{{ genre.name }}</span>
          <span class="genre-stat">
            {{ mode === 'games' ? `${genre.games} jeux` : `${formatOwners(genre.owners)} possesseurs` }}
          </span>
        </div>

        <div class="tags-cloud">
          <div
            v-for="tag in genre.children"
            :key="tag.id"
            class="tag-cell"
            :style="{
              backgroundColor: getScoreColor(tag.score),
              flexGrow: getWeight(tag)
            }"
            :title="`${tag.name} : ${tag.games} jeux, ${formatOwners(tag.owners)} joueurs, note: ${tag.score}/100`"
          >
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-sub">
              {{ mode === 'games' ? `${tag.games} j.` : formatOwners(tag.owners) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface TreemapTagNode {
  id: string
  name: string
  games: number
  owners: number
  score: number
  votes?: number
}

export interface TreemapGenreNode {
  id: string
  name: string
  games: number
  owners: number
  score: number
  children: TreemapTagNode[]
}

const props = defineProps<{
  data: TreemapGenreNode[]
  mode: 'games' | 'players'
}>()

const sortedGenres = computed(() => {
  return [...props.data].sort((a, b) => getWeight(b) - getWeight(a))
})

function getWeight(node: TreemapGenreNode | TreemapTagNode): number {
  if (props.mode === 'players') {
    return Math.max(node.owners || 0, 1)
  }
  return Math.max(node.games || 0, 1)
}

function formatOwners(num: number): string {
  if (!num) return '0'
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(0)}k`
  return num.toString()
}

function getScoreColor(score: number): string {
  if (!score || score <= 0) return '#475569'
  if (score >= 80) return '#059669'
  if (score >= 70) return '#0284c7'
  if (score >= 60) return '#d97706'
  if (score >= 50) return '#ea580c'
  return '#dc2626'
}
</script>

<style scoped>
.treemap-wrapper {
  width: 100%;
}

.treemap-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  min-height: 420px;
}

.genre-block {
  flex-basis: calc(33% - 1.25rem);
  background: #ffffff;
  border: 2px solid #cbd5e1;
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 260px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.genre-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.genre-title {
  font-weight: 800;
  font-size: 1.1rem;
  color: #0f172a;
}

.genre-stat {
  font-size: 0.85rem;
  color: #475569;
  font-weight: 700;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  flex: 1;
}

.tag-cell {
  padding: 0.6rem 0.75rem;
  border-radius: 0.375rem;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: transform 0.15s, opacity 0.15s, box-shadow 0.15s;
  flex-basis: calc(25% - 0.5rem);
  min-width: 65px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.tag-cell:hover {
  transform: translateY(-2px);
  opacity: 0.95;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.25);
}

.tag-name {
  font-size: 0.8rem;
  font-weight: 800;
  text-align: center;
  line-height: 1.15;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
}

.tag-sub {
  font-size: 0.7rem;
  opacity: 0.95;
  font-weight: 600;
  margin-top: 0.15rem;
}
</style>
