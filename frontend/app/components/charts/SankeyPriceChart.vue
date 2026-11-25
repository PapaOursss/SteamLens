<template>
  <ChartFrame :option="option" :height="height" :label="label" />
</template>

<script setup lang="ts">
import type { SankeyLink, SankeyNode } from '~/types'

const PRICE_BRACKETS = ['Gratuit', '< 5 €', '5-15 €', '15-30 €', '> 30 €']
const POSITIVE_OPACITY = 0.6

/** Prix : la rampe séquentielle (ordonnés). Accueil : les couleurs d'état. Genres : neutres. */
function nodeColor(name: string): string {
  const bracket = PRICE_BRACKETS.indexOf(name)
  if (bracket >= 0) return SEQUENTIAL_COLORS[bracket]!
  const verdicts: Record<string, string> = {
    Négatif: STATUS_COLORS.critical,
    Mitigé: STATUS_COLORS.warning,
    Positif: STATUS_COLORS.good,
    'Très positif': STATUS_COLORS.good
  }
  return verdicts[name] ?? COLORS.line
}

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
      color: nodeColor(node.name),
      opacity: node.name === 'Positif' ? POSITIVE_OPACITY : 1,
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
          return `${escapeHtml(params.data.source ?? '')} &rarr; ${escapeHtml(params.data.target ?? '')} : <strong>${formatNumber(params.data.value)}</strong> jeux`
        }
        return `<strong>${escapeHtml(params.data.name ?? '')}</strong>`
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
        nodeGap: 10,
        label: {
          color: COLORS.text,
          fontFamily: FONT_BODY,
          fontSize: 13
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
