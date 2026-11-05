<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Qui sont les joueurs Steam ?</h1>
      <p class="text-sm text-slate-400 mt-1">
        L'enquête matériel et logiciels de Steam, mois après mois : langues, systèmes, cartes
        graphiques, mémoire et casques VR.
      </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <StatTile
        v-for="highlight in survey?.highlights ?? []"
        :key="highlight.label"
        :label="highlight.label"
        :value="latestValue(highlight.values)"
        :hint="lastMonth"
      />
    </div>

    <ChartCard
      :title="CATEGORY_LABELS[category] ?? category"
      subtitle="Part des joueurs interrogés, en %"
      source="Enquête matériel et logiciels de Steam"
      :loading="loading"
      :empty="!survey?.months.length"
      empty-message="Aucune enquête : lancer manage.py import_hardware_survey."
      height="380px"
    >
      <template #actions>
        <select
          v-model="category"
          class="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1"
        >
          <option v-for="(label, key) in CATEGORY_LABELS" :key="key" :value="key">{{ label }}</option>
        </select>
      </template>
      <VChart class="w-full h-96" :option="option" autoresize />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import type { HardwareSurvey } from '~/types'

useHead({ title: 'Enquête matériel Steam — SteamLens' })

const CATEGORY_LABELS: Record<string, string> = {
  language: 'Langues',
  os: "Systèmes d'exploitation",
  gpu: 'Cartes graphiques',
  ram: 'Mémoire vive',
  vr: 'Casques VR'
}

const { get } = useApi()
const category = ref('language')
const survey = ref<HardwareSurvey | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    survey.value = await get<HardwareSurvey>('/stats/hardware-survey/', { category: category.value })
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(category, load)

const lastMonth = computed(() => survey.value?.months.at(-1)?.slice(0, 7) ?? '')

function latestValue(values: (number | null)[]): string {
  const value = [...values].reverse().find((entry) => entry !== null)
  return value === undefined || value === null ? '—' : `${value.toFixed(2)} %`
}

const option = computed(() => ({
  tooltip: { trigger: 'axis', valueFormatter: (value: number) => `${value} %` },
  legend: { type: 'scroll', top: 0, textStyle: { color: '#cbd5e1' } },
  grid: { left: 50, right: 20, top: 40, bottom: 40 },
  xAxis: {
    type: 'category',
    data: (survey.value?.months ?? []).map((month) => month.slice(0, 7)),
    axisLabel: { color: '#94a3b8' }
  },
  yAxis: { type: 'value', axisLabel: { color: '#94a3b8', formatter: '{value} %' } },
  series: (survey.value?.series ?? []).map((series) => ({
    name: series.item,
    type: 'line',
    connectNulls: true,
    data: series.values
  }))
}))
</script>
