<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Historique des prix et soldes</h1>
      <p class="text-sm text-slate-400 mt-1">
        Chaque changement de prix sur Steam depuis des années (IsThereAnyDeal), et le calendrier
        des soldes : on voit revenir celles d'été et d'hiver.
      </p>
    </header>

    <ChartCard
      title="Calendrier des soldes Steam"
      subtitle="Jeux qui passent en promo, par année et semaine"
      source="IsThereAnyDeal"
      :loading="calendarLoading"
      :empty="!calendar?.cells.length"
      empty-message="Aucun historique : lancer manage.py import_itad_history (clé ITAD_API_KEY)."
    >
      <VChart class="w-full h-72" :option="calendarOption" autoresize />
    </ChartCard>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <GameSelector @select="(game) => (selectedAppid = game.appid)" />
      <p v-if="error" class="text-sm text-rose-400">{{ error }}</p>
      <template v-if="history">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatTile label="Plus bas historique" :value="lowestLabel" />
          <StatTile label="Promos" :value="String(history.summary.promotions)" />
          <StatTile label="Promos par an" :value="String(history.summary.promotions_per_year)" />
          <StatTile label="Remise moyenne" :value="`${history.summary.average_cut} %`" />
        </div>
        <ChartCard
          :title="history.name"
          subtitle="Prix sur Steam (France) et prix hors promo"
          source="IsThereAnyDeal"
          :empty="!history.changes.length"
        >
          <VChart class="w-full h-80" :option="historyOption" autoresize />
        </ChartCard>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { PriceHistory, SalesCalendar } from '~/types'

useHead({ title: 'Historique des prix — SteamLens' })

const { get } = useApi()
const calendar = ref<SalesCalendar | null>(null)
const calendarLoading = ref(true)
const selectedAppid = ref<number | null>(null)
const history = ref<PriceHistory | null>(null)
const error = ref('')
const WEEKS_IN_YEAR = 53

onMounted(async () => {
  try {
    calendar.value = await get<SalesCalendar>('/stats/sales-calendar/')
  } finally {
    calendarLoading.value = false
  }
})

watch(selectedAppid, async (appid) => {
  if (appid === null) return
  error.value = ''
  try {
    history.value = await get<PriceHistory>(`/stats/price-history/${appid}/`)
  } catch {
    error.value = "Impossible de charger l'historique de ce jeu."
  }
})

const lowestLabel = computed(() => {
  const summary = history.value?.summary
  if (!summary?.lowest_price) return '—'
  return `${summary.lowest_price.toFixed(2)} ${history.value?.currency ?? ''} (${summary.lowest_date})`
})

const calendarOption = computed(() => {
  const years = calendar.value?.years ?? []
  const cells = calendar.value?.cells ?? []
  return {
    tooltip: {
      formatter: (params: { value: [number, number, number] }) =>
        `Semaine ${params.value[0] + 1} de ${years[params.value[1]]} : ${params.value[2]} jeux en promo`
    },
    grid: { left: 50, right: 20, top: 10, bottom: 60 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: WEEKS_IN_YEAR }, (_, index) => index + 1),
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: { type: 'category', data: years, axisLabel: { color: '#94a3b8' } },
    visualMap: {
      min: 0,
      max: Math.max(1, ...cells.map((cell) => cell[2])),
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      textStyle: { color: '#cbd5e1' },
      inRange: { color: ['#0f172a', '#22d3ee'] }
    },
    series: [
      {
        type: 'heatmap',
        data: cells.map(([year, week, count]) => [week - 1, years.indexOf(year), count])
      }
    ]
  }
})

const historyOption = computed(() => {
  const changes = history.value?.changes ?? []
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Prix payé', 'Prix hors promo'], textStyle: { color: '#cbd5e1' } },
    grid: { left: 50, right: 20, top: 40, bottom: 40 },
    xAxis: { type: 'time', axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
    series: [
      {
        name: 'Prix payé',
        type: 'line',
        step: 'end',
        showSymbol: false,
        data: changes.map((change) => [change.changed_at, change.price])
      },
      {
        name: 'Prix hors promo',
        type: 'line',
        step: 'end',
        showSymbol: false,
        lineStyle: { type: 'dashed' },
        data: changes.map((change) => [change.changed_at, change.regular])
      }
    ]
  }
})
</script>
