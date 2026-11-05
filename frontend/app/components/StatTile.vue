<template>
  <div class="rounded-lg bg-slate-950 border border-slate-800/80 p-3">
    <div class="text-[11px] uppercase tracking-wider text-slate-400">{{ label }}</div>
    <div class="text-lg font-bold text-slate-100 mt-1 tabular-nums">{{ value }}</div>
    <div v-if="hint" class="text-xs text-slate-500 mt-0.5">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint?: string
}>()
</script>
