<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { SankeyLink, SankeyNode } from '~/types'
import { chartBase, escapeHtml } from '~/utils/chartBase'
import { COLORS } from '~/utils/tokens'

const NODE_COLORS: Record<string, string> = {
  // Tranches de prix
  Gratuit: '#50C878',
  '< 5 €': '#2E97D4',
  '5-15 €': '#FFC53D',
  '15-30 €': '#FF7F50',
  '> 30 €': '#E0628F',
  // Accueil
  Négatif: '#D9534F',
  Mitigé: '#F0AD4E',
  Positif: '#5BC0DE',
  'Très positif': '#5CB85C'
}

const DEFAULT_GENRE_COLOR = '#9CA0EC'

const props = withDefaults(
  defineProps<{
    nodes: SankeyNode[]
    links: SankeyLink[]
    height?: number
    label?: string
  }>(),
  {
    height: 560,
    label: 'Diagramme Sankey : Genre vers Tranche de prix vers Accueil'
  }
)

const option = computed(() => {
  const base = chartBase()

  const echartsNodes = props.nodes.map((node) => ({
    name: node.name,
    itemStyle: {
      color: NODE_COLORS[node.name] ?? DEFAULT_GENRE_COLOR,
      borderColor: COLORS.deep,
      borderWidth: 1
    }
  }))

  return {
    ...base,
    tooltip: {
      ...base.tooltip,
      formatter: (params: { dataType: string; data: { name?: string; source?: string; target?: string; value: number } }) => {
        if (params.dataType === 'edge') {
          return `${escapeHtml(params.data.source ?? '')} &rarr; ${escapeHtml(params.data.target ?? '')} : <strong>${params.data.value}</strong> jeux`
        }
        return `Nœud : <strong>${escapeHtml(params.data.name ?? '')}</strong>`
      }
    },
    series: [
      {
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: echartsNodes,
        links: props.links,
        orient: 'horizontal',
        draggable: false,
        label: {
          color: COLORS.text,
          fontSize: 12
        },
        lineStyle: {
          color: 'source',
          curveness: 0.5,
          opacity: 0.35
        }
      }
    ]
  }
})
</script>
