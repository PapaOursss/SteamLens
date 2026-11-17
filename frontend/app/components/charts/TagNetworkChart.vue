<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { TagNetworkEdge, TagNetworkNode } from '~/types'
import { chartBase, escapeHtml } from '~/utils/chartBase'
import { COLORS } from '~/utils/tokens'

const COMMUNITY_COLORS = [
  '#FFC53D',
  '#2E97D4',
  '#E0628F',
  '#50C878',
  '#9CA0EC',
  '#FF7F50',
  '#20B2AA',
  '#DDA0DD',
  '#F4F3FF',
  '#B8860B'
] as const

const props = withDefaults(
  defineProps<{
    nodes: TagNetworkNode[]
    edges: TagNetworkEdge[]
    height?: number
    label?: string
  }>(),
  {
    height: 620,
    label: 'Réseau de co-occurrence des tags Steam'
  }
)

const maxGames = computed(() => {
  if (!props.nodes.length) return 1
  return Math.max(...props.nodes.map((n) => n.games))
})

const option = computed(() => {
  const base = chartBase()

  const categories = COMMUNITY_COLORS.map((color, idx) => ({
    name: `Famille ${idx + 1}`,
    itemStyle: { color }
  }))

  const echartsNodes = props.nodes.map((n) => {
    const sizeRatio = Math.sqrt(n.games / maxGames.value)
    const symbolSize = Math.max(10, Math.min(42, Math.round(10 + sizeRatio * 32)))
    const catIndex = Math.abs(n.community) % COMMUNITY_COLORS.length
    return {
      id: String(n.id),
      name: n.name,
      value: n.games,
      symbolSize,
      category: catIndex,
      label: {
        show: symbolSize > 18,
        color: COLORS.text,
        fontSize: 11
      }
    }
  })

  const echartsLinks = props.edges.map((e) => ({
    source: String(e.source),
    target: String(e.target),
    value: e.weight,
    lineStyle: {
      width: Math.max(1, Math.min(6, Math.round(Math.log2(e.weight)))),
      color: COLORS.line,
      opacity: 0.45,
      curveness: 0.1
    }
  }))

  return {
    ...base,
    tooltip: {
      ...base.tooltip,
      formatter: (params: { dataType: string; data: { name?: string; value: number } }) => {
        if (params.dataType === 'edge') {
          return `Co-occurrence : <strong>${params.data.value}</strong> jeux partagés`
        }
        return `Tag : <strong>${escapeHtml(params.data.name ?? '')}</strong><br>Jeux : <strong>${params.data.value}</strong>`
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: echartsNodes,
        links: echartsLinks,
        categories,
        roam: true,
        label: {
          position: 'right'
        },
        force: {
          repulsion: 90,
          gravity: 0.3,
          edgeLength: [30, 110],
          friction: 0.6
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4,
            opacity: 0.9
          }
        }
      }
    ]
  }
})
</script>
