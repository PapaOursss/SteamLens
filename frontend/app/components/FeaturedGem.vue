<template>
  <div class="gem-banner">
    <div class="gem-badge">💎 Pépite du jour</div>
    <div class="gem-card">
      <img :src="gem.header_image" :alt="gem.name" class="gem-img" />
      <div class="gem-info">
        <h3 class="gem-title">{{ gem.name }}</h3>
        <p class="gem-desc">
          {{ gem.short_description || 'Un jeu indépendant remarquable salué par la communauté Steam.' }}
        </p>
        <div class="gem-meta">
          <span class="gem-price">
            {{ gem.price_eur > 0 ? `${gem.price_eur.toFixed(2)} €` : 'Gratuit' }}
          </span>
          <span class="gem-tag">Très apprécié & Accessible</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DashboardGem } from '~/types/dashboard'

defineProps<{
  gem: DashboardGem
}>()
</script>

<style scoped>
.gem-banner {
  background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 2.5rem;
}
.gem-badge {
  display: inline-block;
  background: #0284c7;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
}
.gem-card {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  flex-wrap: wrap;
}
.gem-img {
  width: 220px;
  height: 105px;
  object-fit: cover;
  border-radius: 0.5rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
}
.gem-info {
  flex: 1;
  min-width: 260px;
}
.gem-title {
  margin: 0 0 0.35rem 0;
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
}
.gem-desc {
  font-size: 0.9rem;
  color: #334155;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}
.gem-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.gem-price {
  font-weight: 800;
  color: #0369a1;
  font-size: 1.1rem;
}
.gem-tag {
  background: #ffffff;
  color: #0f766e;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #ccfbf1;
}
</style>
