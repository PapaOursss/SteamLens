<template>
  <ul class="grid gap-x-8 gap-y-6 md:grid-cols-2 xl:grid-cols-3">
    <li v-for="row in rows" :key="row.item">
      <h3 class="mb-1 flex justify-between gap-4 font-sans text-base font-semibold tracking-normal">
        <span>{{ row.item }}</span>
        <span class="figure shrink-0">{{ formatPercent(row.latest) }}</span>
      </h3>
      <TimeLineChart
        :points="row.points"
        :height="HEIGHT"
        :label="`Part de ${row.item} au fil des mois`"
        :format-value="formatPercent"
        :format-axis="formatPercent"
      />
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { SurveySeries } from '~/types'

const HEIGHT = 160

const props = defineProps<{ months: string[]; series: SurveySeries[] }>()

const rows = computed(() =>
  props.series
    .map((row) => ({
      item: row.item,
      points: row.values.flatMap((value, index) =>
        value === null ? [] : [{ date: props.months[index]!, value }]
      )
    }))
    .filter((row) => row.points.length)
    .map((row) => ({ ...row, latest: row.points.at(-1)!.value }))
)
</script>
