<template>
  <div class="stat-card">
    <div class="card-icon">{{ icon }}</div>
    <div class="card-content">
      <span class="card-label">{{ label }}</span>
      <strong class="card-value">{{ value }}</strong>
      <span v-if="hint" class="card-hint">{{ hint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  icon: string
  hint?: string
}>()
</script>

<style scoped>
.stat-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.card-icon {
  font-size: 2rem;
  background: #eff6ff;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  flex-shrink: 0;
}
.card-content {
  display: flex;
  flex-direction: column;
}
.card-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.card-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
}
.card-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.2rem;
}
</style>
