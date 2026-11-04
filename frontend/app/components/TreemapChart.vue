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
  if (!score || score <= 0) return '#94a3b8'
  if (score >= 80) return '#15803d'
  if (score >= 70) return '#65a30d'
  if (score >= 60) return '#ca8a04'
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
  gap: 1rem;
  min-height: 400px;
}

.genre-block {
  flex-basis: calc(33% - 1rem);
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 250px;
}

.genre-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 0.35rem;
}

.genre-title {
  font-weight: 700;
  font-size: 1rem;
  color: #0f172a;
}

.genre-stat {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 600;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex: 1;
}

.tag-cell {
  padding: 0.4rem 0.6rem;
  border-radius: 0.25rem;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s;
  flex-basis: calc(25% - 0.35rem);
  min-width: 60px;
}

.tag-cell:hover {
  opacity: 0.85;
}

.tag-name {
  font-size: 0.75rem;
  font-weight: 700;
  text-align: center;
  line-height: 1.1;
}

.tag-sub {
  font-size: 0.65rem;
  opacity: 0.9;
}
</style>
