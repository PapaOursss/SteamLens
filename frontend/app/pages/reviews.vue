<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Avis Steam et review bombings</h1>
      <p class="text-sm text-slate-400 mt-1">
        Ratio d'avis positifs par langue, courbe semaine par semaine et chutes brutales repérées.
        Seuls des comptes sont gardés : ni auteur ni SteamID.
      </p>
    </header>

    <ChartCard
      title="Review bombings repérés"
      subtitle="Semaines où le ratio positif chute d'au moins 20 points sous les 4 précédentes"
      source="Steam Store (appreviews)"
      :loading="bombingsLoading"
      :empty="!bombings.length"
      empty-message="Aucune chute brutale repérée (ou import_reviews pas encore lancé)."
      height="120px"
    >
      <ul class="w-full divide-y divide-slate-800/60 text-sm">
        <li v-for="row in bombings" :key="`${row.appid}-${row.week_start}`" class="flex justify-between py-2">
          <span class="text-slate-100 font-semibold">{{ row.name }}</span>
          <span class="text-slate-400">semaine du {{ row.week_start }}</span>
          <span class="text-rose-400 font-bold">
            {{ percent(row.baseline_share) }} → {{ percent(row.positive_share) }}
          </span>
        </li>
      </ul>
    </ChartCard>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <GameSelector @select="(game) => (selectedAppid = game.appid)" />
      <p v-if="error" class="text-sm text-rose-400">{{ error }}</p>
      <div v-if="reviews" class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard title="Ratio positif par langue" source="Steam Store" :empty="!reviews.languages.length">
          <VChart class="w-full h-80" :option="languageOption" autoresize />
        </ChartCard>
        <ChartCard
          title="Ratio positif par semaine"
          :subtitle="`${reviews.bombings.length} review bombing(s) repéré(s)`"
          source="Steam Store"
          :empty="!reviews.weeks.length"
        >
          <VChart class="w-full h-80" :option="weeklyOption" autoresize />
        </ChartCard>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { BombedGame, GameReviews } from '~/types'

useHead({ title: 'Avis Steam — SteamLens' })

const { get } = useApi()
const bombings = ref<BombedGame[]>([])
const bombingsLoading = ref(true)
const selectedAppid = ref<number | null>(null)
const reviews = ref<GameReviews | null>(null)
const error = ref('')
const PERCENT = 100

function percent(share: number): string {
  return `${Math.round(share * PERCENT)} %`
}

onMounted(async () => {
  try {
    bombings.value = await get<BombedGame[]>('/stats/review-bombings/')
  } finally {
    bombingsLoading.value = false
  }
})

watch(selectedAppid, async (appid) => {
  if (appid === null) return
  error.value = ''
  try {
    reviews.value = await get<GameReviews>(`/stats/reviews/${appid}/`)
  } catch {
    error.value = 'Impossible de charger les avis de ce jeu.'
  }
})

const axisLabel = { color: '#94a3b8' }

const languageOption = computed(() => {
  const languages = [...(reviews.value?.languages ?? [])].sort((a, b) => a.positive_share - b.positive_share)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 90, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'value', min: 0, max: PERCENT, axisLabel },
    yAxis: { type: 'category', data: languages.map((row) => row.language), axisLabel },
    series: [
      {
        type: 'bar',
        itemStyle: { color: '#22d3ee' },
        data: languages.map((row) => Math.round(row.positive_share * PERCENT))
      }
    ]
  }
})

const weeklyOption = computed(() => {
  const weeks = reviews.value?.weeks ?? []
  const bombed = new Set((reviews.value?.bombings ?? []).map((row) => row.week_start))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 10, bottom: 40 },
    xAxis: { type: 'category', data: weeks.map((week) => week.week_start), axisLabel },
    yAxis: { type: 'value', min: 0, max: PERCENT, axisLabel },
    series: [
      {
        type: 'line',
        smooth: true,
        data: weeks.map((week) => ({
          value: Math.round(week.positive_share * PERCENT),
          itemStyle: { color: bombed.has(week.week_start) ? '#f43f5e' : '#22d3ee' },
          symbolSize: bombed.has(week.week_start) ? 12 : 4
        }))
      }
    ]
  }
})
</script>
