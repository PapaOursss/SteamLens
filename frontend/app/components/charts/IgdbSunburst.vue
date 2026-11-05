<template>
  <ChartFrame :option="option" :height="600" label="Sunburst IGDB : genre, thème, mode de jeu" />
</template>

<script setup lang="ts">
import type { SunburstNode } from '~/types'
import type { GenreMetric } from '~/components/charts/GenreTreemap.vue'

interface SunburstTooltipParam {
  name: string
  data: { games: number; owners: number }
}

const props = defineProps<{ nodes: SunburstNode[]; metric: GenreMetric }>()

function toSeriesNode(node: SunburstNode): object {
  return {
    name: node.name,
    value: node[props.metric],
    games: node.games,
    owners: node.owners,
    children: node.children?.map(toSeriesNode)
  }
}

function tooltipText({ name, data }: SunburstTooltipParam): string {
  return `<strong>${escapeHtml(name)}</strong><br>${formatNumber(data.games)} jeux<br>${formatCompact(data.owners)} possesseurs estimés`
}

const ringLevel = (fill: string, ink: string) => ({
  itemStyle: { color: fill, borderColor: COLORS.ground, borderWidth: 2 },
  label: { color: ink, fontFamily: FONT_BODY, minAngle: 8 }
})

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, formatter: tooltipText },
  series: [
    {
      type: 'sunburst',
      data: props.nodes.map(toSeriesNode),
      radius: ['12%', '96%'],
      sort: null,
      levels: [
        {},
        ringLevel(SEQUENTIAL_COLORS[4], COLORS.deep),
        ringLevel(SEQUENTIAL_COLORS[2], COLORS.deep),
        ringLevel(SEQUENTIAL_COLORS[1], COLORS.text)
      ]
    }
  ]
}))
</script>
