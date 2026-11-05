<template>
  <div>
    <ChartFrame :option="option" :height="620" label="Treemap des genres Steam et de leurs tags" />
    <ul class="mt-3 flex flex-wrap gap-x-5 gap-y-2" aria-label="Légende : note moyenne Metacritic">
      <li class="text-soft">Note moyenne</li>
      <li v-for="level in legend" :key="level.label" class="flex items-center gap-2">
        <span class="h-3 w-6 rounded-sm" :style="{ backgroundColor: level.fill }" aria-hidden="true" />
        {{ level.label }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { TreemapGenre, TreemapTag } from '~/types'

export type GenreMetric = 'games' | 'owners'

interface TreemapTooltipParam {
  name: string
  data: { games: number; owners: number; score: number }
}

const UPPER_LABEL_HEIGHT = 28
const TILE_GAP = 2

const props = defineProps<{ genres: TreemapGenre[]; metric: GenreMetric }>()

const legend = [...SCORE_LEVELS, NO_SCORE_LEVEL]

function tagNode(tag: TreemapTag) {
  const level = scoreLevel(tag.score)
  return {
    name: tag.name,
    value: tag[props.metric],
    games: tag.games,
    owners: tag.owners,
    score: tag.score,
    itemStyle: { color: level.fill },
    label: { color: level.ink }
  }
}

const nodes = computed(() =>
  props.genres
    .map((genre) => ({
      name: genre.name,
      games: genre.games,
      owners: genre.owners,
      score: genre.score,
      itemStyle: { color: COLORS.raised },
      children: genre.children.map(tagNode).filter((tag) => tag.value > 0)
    }))
    .filter((genre) => genre.children.length)
)

function tooltipText({ name, data }: TreemapTooltipParam): string {
  const score = data.score > 0 ? `<br>Note moyenne : ${data.score}` : ''
  return `<strong>${escapeHtml(name)}</strong><br>${formatNumber(data.games)} jeux<br>${formatCompact(data.owners)} possesseurs estimés${score}`
}

const option = computed(() => ({
  ...chartBase(),
  tooltip: { ...chartBase().tooltip, formatter: tooltipText },
  series: [
    {
      type: 'treemap',
      name: 'Tous les genres',
      data: nodes.value,
      left: 0,
      right: 0,
      top: 0,
      bottom: 36,
      roam: false,
      nodeClick: 'zoomToNode',
      breadcrumb: {
        bottom: 0,
        left: 0,
        itemStyle: { color: COLORS.raised, borderColor: COLORS.ground, textStyle: { color: COLORS.text } },
        emphasis: { itemStyle: { color: COLORS.line } }
      },
      label: { fontFamily: FONT_BODY, fontSize: 13 },
      upperLabel: { show: true, height: UPPER_LABEL_HEIGHT, color: COLORS.text, fontFamily: FONT_BODY, fontWeight: 600 },
      itemStyle: { borderColor: COLORS.ground, borderWidth: 1, gapWidth: TILE_GAP },
      levels: [
        { itemStyle: { borderColor: COLORS.ground, borderWidth: 2, gapWidth: TILE_GAP } },
        { colorSaturation: null, itemStyle: { borderColorSaturation: null, gapWidth: 1 } }
      ]
    }
  ]
}))
</script>
