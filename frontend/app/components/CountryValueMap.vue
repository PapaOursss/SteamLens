<template>
  <ClientOnly>
    <VChart v-if="registered" class="w-full" :style="{ height }" :option="option" autoresize />
    <template #fallback>
      <div class="flex items-center justify-center text-xs text-slate-400" :style="{ height }">
        Chargement de la carte…
      </div>
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
import { registerMap } from 'echarts/core'

interface GeoFeature {
  properties: { iso3: string; name: string }
}

const props = withDefaults(
  defineProps<{
    values: Record<string, number>
    unit?: string
    height?: string
  }>(),
  { unit: '', height: '440px' }
)

const registered = ref(false)
const namesByIso3 = ref<Record<string, string>>({})

onMounted(async () => {
  const geo = await $fetch<{ features: GeoFeature[] }>('/world-110m.json')
  registerMap('world', geo as unknown as Parameters<typeof registerMap>[1])
  namesByIso3.value = Object.fromEntries(
    geo.features.map((feature) => [feature.properties.iso3, feature.properties.name])
  )
  registered.value = true
})

const mapData = computed(() =>
  Object.entries(props.values).map(([iso3, value]) => ({
    name: namesByIso3.value[iso3] ?? iso3,
    value
  }))
)

const maxValue = computed(() => Math.max(1, ...mapData.value.map((row) => row.value)))

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: { name: string; value: number | undefined }) =>
      Number.isFinite(params.value) ? `${params.name}<br/>${params.value} ${props.unit}` : params.name
  },
  visualMap: {
    min: 0,
    max: maxValue.value,
    left: 'left',
    bottom: '5%',
    calculable: true,
    textStyle: { color: '#cbd5e1' },
    inRange: { color: ['#164e63', '#22d3ee'] }
  },
  series: [
    {
      type: 'map',
      map: 'world',
      roam: true,
      itemStyle: { areaColor: '#1e293b', borderColor: '#334155' },
      emphasis: { label: { show: false }, itemStyle: { areaColor: '#f59e0b' } },
      data: mapData.value
    }
  ]
}))
</script>
