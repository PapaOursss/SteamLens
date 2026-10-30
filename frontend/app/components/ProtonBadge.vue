<template>
  <span class="proton-badge" :class="tierClass" :title="tooltip">
    <span class="badge-icon">●</span>
    <span class="badge-tier">{{ label }}</span>
    <span v-if="score !== undefined" class="badge-score">{{ (score * 100).toFixed(0) }}%</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    tier: 'native' | 'platinum' | 'gold' | 'silver' | 'bronze' | 'borked' | 'pending' | string
    score?: number
    totalReports?: number
  }>(),
  {
    tier: 'pending',
    score: undefined,
    totalReports: 0
  }
)

const tierClass = computed(() => `tier-${props.tier.toLowerCase()}`)

const label = computed(() => {
  const map: Record<string, string> = {
    native: 'Native Linux',
    platinum: 'Platinum',
    gold: 'Gold',
    silver: 'Silver',
    bronze: 'Bronze',
    borked: 'Borked',
    pending: 'En attente'
  }
  return map[props.tier.toLowerCase()] || props.tier
})

const tooltip = computed(() => {
  return `Compatibilité Steam Deck / Proton : ${label.value} (${props.totalReports} retours)`
})
</script>

<style scoped>
.proton-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid transparent;
}
.badge-icon { font-size: 0.6rem; }
.badge-score { opacity: 0.8; font-weight: 500; font-size: 0.7rem; }

.tier-native { background: #dcfce7; color: #15803d; border-color: #86efac; }
.tier-platinum { background: #e0e7ff; color: #4338ca; border-color: #a5b4fc; }
.tier-gold { background: #fef9c3; color: #a16207; border-color: #fde047; }
.tier-silver { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.tier-bronze { background: #ffedd5; color: #c2410c; border-color: #fdba74; }
.tier-borked { background: #fee2e2; color: #b91c1c; border-color: #fca5a5; }
.tier-pending { background: #f3f4f6; color: #6b7280; border-color: #e5e7eb; }
</style>
