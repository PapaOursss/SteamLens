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

.tier-native { background: #052e16; color: #4ade80; border-color: #166534; }
.tier-platinum { background: #1e1b4b; color: #a5b4fc; border-color: #3730a3; }
.tier-gold { background: #422006; color: #fde047; border-color: #854d0e; }
.tier-silver { background: #1e293b; color: #cbd5e1; border-color: #475569; }
.tier-bronze { background: #431407; color: #fdba74; border-color: #9a3412; }
.tier-borked { background: #450a0a; color: #f87171; border-color: #991b1b; }
.tier-pending { background: #1e293b; color: #94a3b8; border-color: #334155; }
</style>
