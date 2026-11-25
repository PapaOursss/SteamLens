<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
export interface RatingPoint {
  appid: number
  name: string
  steam_score: number
  press_score: number
  rawg_rating: number | null
}

const props = withDefaults(
  defineProps<{
    points: RatingPoint[]
    height?: number
    label: string
  }>(),
  { height: 450 }
)

const option = computed(() => {
  const scatterData = props.points.map((p) => [p.press_score, p.steam_score, p])

  return {
    tooltip: {
      formatter(params: { data: [number, number, RatingPoint] }) {
        const item = params.data[2]
        let res = `<strong>${escapeHtml(item.name)}</strong><br/>`
        res += `Metacritic (Presse) : <strong>${item.press_score}/100</strong><br/>`
        res += `Steam (Joueurs) : <strong>${item.steam_score}%</strong>`
        if (item.rawg_rating) {
          res += `<br/>Note RAWG : <strong>${item.rawg_rating}/5</strong>`
        }
        return res
      }
    },
    grid: { left: 50, right: 30, top: 40, bottom: 50 },
    xAxis: {
      type: 'value',
      name: 'Metacritic',
      nameLocation: 'middle',
      nameGap: 30,
      min: 40,
      max: 100
    },
    yAxis: {
      type: 'value',
      name: 'Avis Steam (%)',
      nameLocation: 'middle',
      nameGap: 35,
      min: 40,
      max: 100
    },
    series: [
      {
        name: 'Accord parfait',
        type: 'line',
        data: [
          [40, 40],
          [100, 100]
        ],
        lineStyle: { type: 'dashed', color: '#6EE7B7', width: 2 },
        symbol: 'none',
        tooltip: { show: false }
      },
      {
        name: 'Jeux',
        type: 'scatter',
        symbolSize: 10,
        itemStyle: {
          color: '#38BDF8',
          opacity: 0.8
        },
        data: scatterData
      }
    ]
  }
})
</script>
