<template>
  <div>
    <PageIntro title="Les pays déclarés des profils" is-lab>
      Le pays affiché, quand il l'est, sur les profils publics des auteurs d'avis récents. Aucun SteamID ni pseudo n'est enregistré : seulement des comptes par pays.
    </PageIntro>

    <div v-if="sample" class="gutter grid grid-cols-2 gap-x-8 gap-y-4 lg:grid-cols-4">
      <StatTile label="Profils lus" :value="formatNumber(sample.profiles)" :hint="sample.date ? formatDate(sample.date) : undefined" />
      <StatTile label="Jeux échantillonnés" :value="formatNumber(sample.games)" />
      <StatTile label="Sans pays déclaré" :value="shareLabel(sample.without_country_share)" :hint="`${formatNumber(sample.without_country)} profils`" />
      <StatTile label="Pays hors carte" :value="formatNumber(sample.unmapped_country)" />
    </div>

    <DataBlock
      title="Profils par pays déclaré"
      note="Source : Steam Web API. Un échantillon, pas la population de Steam."
      :is-loading="mapLoading"
      :has-error="mapError"
      :is-empty="!values.length"
      empty-message="Pas encore d'échantillon : l'import des profils n'a pas tourné sur cette base."
      :height="520"
      @retry="refreshMap()"
    >
      <WorldValueMap :values="values" :format-value="formatProfiles" label="Carte du nombre de profils par pays déclaré" />
    </DataBlock>

    <DataBlock
      v-if="stats?.countries.length || isLoading"
      title="Pays les plus représentés"
      :is-loading="isLoading"
      :has-error="hasError"
      @retry="refresh()"
    >
      <div class="max-w-3xl"><RankBars :rows="countryRows" /></div>
    </DataBlock>

    <DataBlock v-if="stats?.by_genre.length" title="Pays dominant par genre">
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Genre</th>
              <th scope="col">Pays dominant</th>
              <th scope="col">Part</th>
              <th scope="col">Profils</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in stats.by_genre" :key="row.genre">
              <td class="font-semibold">{{ row.genre }}</td>
              <td>{{ row.top_country }}</td>
              <td class="figure">{{ shareLabel(row.top_country_share) }}</td>
              <td class="figure">{{ formatNumber(row.profiles) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { ProfileCountries, RankRow, WorldMapData } from '~/types'

const PERCENT = 100

useHead({ title: 'Pays des profils' })

const { data: stats, isLoading, hasError, refresh } = useApiResource<ProfileCountries>('/stats/profile-countries/')
const {
  data: mapData,
  isLoading: mapLoading,
  hasError: mapError,
  refresh: refreshMap
} = useApiResource<WorldMapData>('/map/profile-countries/')

const sample = computed(() => stats.value?.sample)

function shareLabel(share: number): string {
  return formatPercent(Math.round(share * PERCENT))
}

function formatProfiles(count: number): string {
  return `${formatNumber(count)} profils`
}

const values = computed(() =>
  Object.entries(mapData.value ?? {}).map(([iso3, value]) => ({ iso3, value }))
)

const countryRows = computed<RankRow[]>(() =>
  (stats.value?.countries ?? []).map((country) => ({
    key: country.iso3,
    label: country.name,
    value: country.profiles,
    display: `${formatNumber(country.profiles)} · ${shareLabel(country.share)}`
  }))
)
</script>
