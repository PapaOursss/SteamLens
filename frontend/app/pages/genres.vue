<template>
  <div>
    <PageIntro title="Ce que Steam met dans ses jeux">
      Chaque genre et ses tags les plus courants. Touchez un genre pour l'ouvrir en grand.
    </PageIntro>

    <div class="gutter">
      <SegmentedControl v-model="metric" label="Mesure de la surface" :options="METRICS" />
    </div>

    <DataBlock
      title="Genres et tags"
      note="SteamSpy (possesseurs estimés, tags) et Metacritic (notes)."
      :is-loading="treemapLoading"
      :has-error="treemapError"
      :is-empty="!treemap?.children.length"
      :height="620"
      @retry="refreshTreemap()"
    >
      <GenreTreemap :genres="treemap!.children" :metric="metric" />
    </DataBlock>

    <DataBlock
      title="Évolution des genres par année de sortie"
      note="Nombre annuel de sorties par genre (ThemeRiver) et moments clés de l'écosystème Steam."
      :is-loading="streamgraphLoading"
      :has-error="streamgraphError"
      :is-empty="!streamgraph?.years.length"
      empty-message="Pas encore de dates de sortie disponibles."
      :height="520"
      @retry="refreshStreamgraph()"
    >
      <GenreStreamgraph
        :years="streamgraph!.years"
        :genres="streamgraph!.genres"
        :series="streamgraph!.series"
        :events="streamgraph!.events"
        label="Évolution des genres par année de sortie sur Steam"
      />
      <div v-if="streamgraph?.events?.length" class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="event in streamgraph.events"
          :key="event.year"
          class="rounded-lg border border-line/40 bg-deep/50 p-3 text-xs"
        >
          <div class="flex items-center gap-1.5 font-semibold text-hot">
            <span>{{ event.year }}</span>
            <span>·</span>
            <span>{{ event.title }}</span>
          </div>
          <p class="mt-1 text-soft">{{ event.description }}</p>
        </div>
      </div>
    </DataBlock>

    <DataBlock
      title="Genres, thèmes et modes selon IGDB"
      note="Du centre vers le bord : genre, thème, mode de jeu."
      :is-loading="sunburstLoading"
      :has-error="sunburstError"
      :is-empty="!sunburst?.children.length"
      empty-message="Pas encore de données : l'import IGDB n'a pas tourné sur cette base."
      :height="600"
      @retry="refreshSunburst()"
    >
      <IgdbSunburst :nodes="sunburst!.children" :metric="metric" />
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { GenreMetric } from '~/components/charts/GenreTreemap.vue'
import type { ChoiceOption, StreamgraphResponse, SunburstResponse, TreemapResponse } from '~/types'

const METRICS: ChoiceOption<GenreMetric>[] = [
  { value: 'games', label: 'Nombre de jeux' },
  { value: 'owners', label: 'Possesseurs' }
]

useHead({ title: 'Genres' })

const metric = ref<GenreMetric>('games')

const {
  data: treemap,
  isLoading: treemapLoading,
  hasError: treemapError,
  refresh: refreshTreemap
} = useApiResource<TreemapResponse>('/stats/treemap/')

const {
  data: streamgraph,
  isLoading: streamgraphLoading,
  hasError: streamgraphError,
  refresh: refreshStreamgraph
} = useApiResource<StreamgraphResponse>('/stats/streamgraph/')

const {
  data: sunburst,
  isLoading: sunburstLoading,
  hasError: sunburstError,
  refresh: refreshSunburst
} = useApiResource<SunburstResponse>('/stats/sunburst-igdb/')
</script>
