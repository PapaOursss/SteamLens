<template>
  <div class="game-row">
    <span class="rank-number">#{{ rank }}</span>
    <img :src="game.header_image" :alt="game.name" class="row-cover" />
    <div class="row-info">
      <span class="row-name">{{ game.name }}</span>
      <div class="bar-container">
        <div class="bar-active" :style="{ width: `${barWidth}%` }"></div>
      </div>
    </div>
    <div class="row-sparkline">
      <span class="sparkline-title">24h</span>
      <SparkLine :values="game.sparkline" :width="110" :height="28" />
    </div>
    <div class="row-players">
      <span class="players-value">{{ formattedPlayers }}</span>
      <span class="players-label">joueurs</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SparkLine from '~/components/SparkLine.vue'
import type { DashboardTopGame } from '~/types/dashboard'

const props = defineProps<{
  game: DashboardTopGame
  rank: number
  maxPlayers: number
}>()

const barWidth = computed(() => {
  const max = props.maxPlayers > 0 ? props.maxPlayers : 1
  return Math.max(5, Math.min(100, (props.game.players / max) * 100))
})

const formattedPlayers = computed(() => {
  return (props.game.players || 0).toLocaleString('fr-FR')
})
</script>

<style scoped>
.game-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  transition: background 0.15s ease;
}
.game-row:hover { background: #f3f4f6; }
.rank-number {
  font-size: 1.1rem;
  font-weight: 800;
  color: #6b7280;
  width: 32px;
  text-align: center;
}
.row-cover {
  width: 90px;
  height: 42px;
  object-fit: cover;
  border-radius: 0.35rem;
  flex-shrink: 0;
}
.row-info { flex: 1; min-width: 140px; }
.row-name {
  display: block;
  font-weight: 700;
  font-size: 0.95rem;
  color: #111827;
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-container {
  height: 8px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}
.bar-active {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border-radius: 9999px;
  transition: width 0.5s ease;
}
.row-sparkline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}
.sparkline-title {
  font-size: 0.65rem;
  color: #9ca3af;
  font-weight: 600;
  text-transform: uppercase;
}
.row-players { text-align: right; min-width: 95px; }
.players-value {
  display: block;
  font-weight: 800;
  font-size: 1rem;
  color: #111827;
}
.players-label { font-size: 0.7rem; color: #6b7280; }
</style>
