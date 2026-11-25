<template>
  <div>
    <PageIntro title="À quoi joue-t-on, selon le pays ?" is-lab>
      Le genre le plus surreprésenté de chaque pays par rapport à la moyenne mondiale. Cliquez un pays pour voir ses dix genres.
    </PageIntro>

    <DataBlock
      title="Genre le plus surreprésenté"
      note="Avis Steam par langue, reportés sur les pays qui parlent cette langue."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.countries.length"
      empty-message="Pas encore d'avis par langue : l'import des avis n'a pas tourné sur cette base."
      :height="620"
      @retry="refresh()"
    >
      <GenreCountryMap v-if="data" :genres="data.genres" :countries="data.countries" @select="selected = $event" />
    </DataBlock>

    <DataBlock v-if="country" :title="country.name" :note="countryNote">
      <template #actions>
        <label class="flex items-center gap-2">
          <span class="text-soft">Pays</span>
          <select v-model="selected" class="field">
            <option v-for="row in data?.countries" :key="row.iso3" :value="row.iso3">{{ row.name }}</option>
          </select>
        </label>
      </template>
      <div class="max-w-3xl"><RankBars :rows="rows" /></div>
    </DataBlock>

    <DataBlock title="Comment c'est calculé, et pourquoi c'est approximatif">
      <div class="max-w-prose space-y-3 leading-relaxed text-soft">
        <p>Steam ne publie pas le pays de ses joueurs. Nous comptons les avis par langue et les rattachons aux pays qui la parlent.</p>
        <p>L'indice compare la part d'un genre dans le pays à sa part mondiale : 1 veut dire « comme partout », 2 « deux fois plus ».</p>
        <p>Deux pays de même langue ont donc la même couleur : l'Argentine et l'Espagne ne se distinguent pas. Beaucoup de joueurs écrivent aussi en anglais. Les langues des streams Twitch ne sont pas encore prises en compte.</p>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { GenresByCountry, RankRow } from '~/types'

useHead({ title: 'Genres par pays' })

const { data, isLoading, hasError, refresh } = useApiResource<GenresByCountry>('/stats/genres-by-country/')
const selected = ref('FRA')

const country = computed(
  () => data.value?.countries.find((row) => row.iso3 === selected.value) ?? data.value?.countries[0]
)
const countryNote = computed(() =>
  country.value
    ? `Environ ${formatNumber(country.value.reviews)} avis rattachés. Langues : ${country.value.languages.map(languageName).join(', ')}.`
    : ''
)
const rows = computed<RankRow[]>(() =>
  (country.value?.genres ?? []).map((row) => ({
    key: row.genre,
    label: row.genre,
    value: row.index,
    display: `× ${formatNumber(Math.round(row.index * 100) / 100)} · ${formatPercent(Math.round(row.share * 100))}`
  }))
)
</script>
