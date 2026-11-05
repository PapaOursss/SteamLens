<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Les jeux que personne ne finit</h1>
      <p class="text-sm text-slate-400 mt-1">
        Part des joueurs qui débloquent chaque succès : la courbe d'abandon montre où ils lâchent,
        le succès de fin d'histoire donne le taux de fin.
      </p>
    </header>

    <ChartCard
      title="Plus faibles taux de fin"
      subtitle="Part des joueurs qui ont le succès de fin d'histoire"
      source="Steam Web API"
      :loading="rankingLoading"
      :empty="!ranking.length"
      empty-message="Aucun succès de fin repéré : lancer manage.py import_achievements."
      height="160px"
    >
      <table class="w-full text-sm text-left">
        <thead class="text-xs text-slate-400 border-b border-slate-800">
          <tr>
            <th class="p-2">Jeu</th>
            <th class="p-2">Taux de fin</th>
            <th class="p-2">Succès médian</th>
            <th class="p-2">Succès</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60 text-slate-200">
          <tr
            v-for="game in ranking"
            :key="game.appid"
            class="cursor-pointer hover:bg-slate-800/40"
            @click="selectedAppid = game.appid"
          >
            <td class="p-2 font-semibold">{{ game.name }}</td>
            <td class="p-2 text-rose-400 font-bold">{{ game.completion_rate.toFixed(1) }} %</td>
            <td class="p-2">{{ game.median_percent.toFixed(1) }} %</td>
            <td class="p-2">{{ game.achievements }}</td>
          </tr>
        </tbody>
      </table>
    </ChartCard>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <GameSelector @select="(game) => (selectedAppid = game.appid)" />
      <p v-if="error" class="text-sm text-rose-400">{{ error }}</p>
      <template v-if="details">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <StatTile
            label="Taux de fin"
            :value="details.completion_rate === null ? 'non repéré' : `${details.completion_rate} %`"
          />
          <StatTile
            label="Plus gros décrochage"
            :value="details.biggest_drop ? `−${details.biggest_drop.drop} points` : '—'"
            :hint="dropHint"
          />
        </div>
        <ChartCard
          :title="`Courbe d'abandon — ${details.name}`"
          subtitle="Succès du plus courant au plus rare ; en rouge, la fin de l'histoire"
          source="Steam Web API"
          :empty="!details.curve.length"
        >
          <VChart class="w-full h-80" :option="curveOption" autoresize />
        </ChartCard>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { GameAchievements, LeastFinishedGame } from '~/types'

useHead({ title: 'Succès Steam — SteamLens' })

const { get } = useApi()
const ranking = ref<LeastFinishedGame[]>([])
const rankingLoading = ref(true)
const selectedAppid = ref<number | null>(null)
const details = ref<GameAchievements | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    ranking.value = await get<LeastFinishedGame[]>('/stats/least-finished/')
  } finally {
    rankingLoading.value = false
  }
})

watch(selectedAppid, async (appid) => {
  if (appid === null) return
  error.value = ''
  try {
    details.value = await get<GameAchievements>(`/stats/achievements/${appid}/`)
  } catch {
    error.value = 'Impossible de charger les succès de ce jeu.'
  }
})

const dropHint = computed(() => {
  const drop = details.value?.biggest_drop
  return drop ? `entre « ${drop.from_achievement} » et « ${drop.to_achievement} »` : undefined
})

const curveOption = computed(() => {
  const curve = details.value?.curve ?? []
  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params: { dataIndex: number }[]) => {
        const step = curve[params[0]?.dataIndex ?? 0]
        return step ? `${step.name}<br/>${step.percent} % des joueurs` : ''
      }
    },
    grid: { left: 50, right: 20, top: 10, bottom: 40 },
    xAxis: { type: 'category', data: curve.map((step) => step.rank), axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: '#94a3b8', formatter: '{value} %' } },
    series: [
      {
        type: 'line',
        areaStyle: { opacity: 0.15 },
        data: curve.map((step) => ({
          value: step.percent,
          itemStyle: { color: step.is_ending ? '#f43f5e' : '#22d3ee' },
          symbolSize: step.is_ending ? 12 : 4
        }))
      }
    ]
  }
})
</script>
