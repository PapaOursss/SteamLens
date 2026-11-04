<template>
  <svg :width="width" :height="height" class="sparkline-svg" :viewBox="`0 0 ${width} ${height}`">
    <polyline
      fill="none"
      :stroke="color"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      :points="pointsString"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    values: number[]
    width?: number
    height?: number
    color?: string
  }>(),
  {
    width: 120,
    height: 32,
    color: '#3b82f6',
  }
)

const pointsString = computed(() => {
  const data = props.values
  if (!data || data.length === 0) return ''
  if (data.length === 1) return `0,${props.height / 2} ${props.width},${props.height / 2}`

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const step = props.width / (data.length - 1)
  const pad = 4
  const h = props.height - pad * 2

  return data
    .map((val, i) => {
      const x = i * step
      const y = props.height - pad - ((val - min) / range) * h
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
})
</script>

<style scoped>
.sparkline-svg {
  display: block;
  overflow: visible;
}
</style>
