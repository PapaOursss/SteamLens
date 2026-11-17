<template>
  <div v-if="activeInfo" class="region-detail-card" :style="{ borderColor: activeInfo.color }">
    <div class="card-header">
      <div class="title-with-badge">
        <span class="region-pill" :style="{ backgroundColor: activeInfo.color }">
          {{ activeInfo.code.toUpperCase() }}
        </span>
        <h3 class="region-title">{{ activeInfo.name }}</h3>
      </div>
      <div class="sales-metric">
        <span class="metric-num">{{ activeInfo.totalSales }} M</span>
        <span class="metric-label">exemplaires vendus</span>
      </div>
    </div>

    <div class="card-body">
      <div class="detail-col">
        <h4 class="sub-heading">🎯 Profil culturel</h4>
        <p class="summary-text">{{ activeInfo.description }}</p>
        <div class="favorite-row">
          <span class="fav-label">Genre n°1 :</span>
          <span class="fav-value" :style="{ color: activeInfo.color }">
            {{ activeInfo.topGenre }} ({{ activeInfo.topGenreShare }})
          </span>
        </div>
      </div>

      <div class="detail-col">
        <h4 class="sub-heading">📊 Top 3 des genres plébiscités</h4>
        <div class="genre-bars">
          <div v-for="item in activeInfo.topGenres" :key="item.genre" class="genre-bar-item">
            <div class="bar-labels">
              <span class="item-genre">{{ item.genre }}</span>
              <span class="item-vol">{{ item.volume }} M</span>
            </div>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{
                  width: (item.volume / activeInfo.maxGenreVolume * 100) + '%',
                  backgroundColor: activeInfo.color
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="detail-col">
        <h4 class="sub-heading">⭐ Hits emblématiques</h4>
        <ul class="hit-list">
          <li v-for="hit in activeInfo.hits" :key="hit" class="hit-item">
            {{ hit }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RegionDetails } from '~/types/regionalSales'

defineProps<{
  activeInfo: RegionDetails | null
}>()
</script>

<style scoped>
.region-detail-card {
  background: #ffffff;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: border-color 0.25s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.region-pill {
  color: white;
  font-weight: 800;
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 0.35rem;
  letter-spacing: 0.5px;
}

.region-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.sales-metric {
  text-align: right;
}

.metric-num {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}

.metric-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.card-body {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.sub-heading {
  margin: 0 0 0.6rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #334155;
}

.summary-text {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 0.8rem 0;
}

.favorite-row {
  font-size: 0.875rem;
}

.fav-label {
  color: #475569;
  font-weight: 600;
}

.fav-value {
  font-weight: 700;
  margin-left: 0.35rem;
}

.genre-bars {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.genre-bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e293b;
}

.item-vol {
  color: #64748b;
}

.bar-track {
  height: 8px;
  background: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.hit-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.hit-item {
  font-size: 0.85rem;
  color: #334155;
  background: #f8fafc;
  padding: 0.35rem 0.65rem;
  border-radius: 0.35rem;
  border-left: 3px solid #cbd5e1;
}
</style>
