<template>
  <div>
    <PageIntro title="D'où viennent les studios ?" is-lab>
      Les jeux Steam les plus possédés, rangés par pays du studio qui les a développés, et le genre que chaque pays fait plus que les autres.
    </PageIntro>

    <SampleNotice v-if="data?.is_sample" class="mb-2">
      L'import Wikidata n'a pas encore tourné : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <DataBlock
      title="Jeux par pays du studio"
      note="Pays des studios selon Wikidata, complété par IGDB. Un jeu fait par deux studios de pays différents compte dans les deux pays."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!mapValues.length"
      empty-message="Aucun studio n'a encore de pays."
      :height="620"
      @retry="refresh()"
    >
      <WorldValueMap :values="mapValues" :format-value="formatGames" label="Carte du nombre de jeux par pays du studio" />
    </DataBlock>

    <DataBlock
      title="Le genre de prédilection de chaque pays"
      :note="`Le genre le plus surreprésenté par rapport à l'ensemble des pays (×2 = deux fois plus fréquent qu'ailleurs), pour les pays d'au moins ${MIN_GAMES} jeux.`"
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!countries.length"
      @retry="refresh()"
    >
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th scope="col">Pays</th>
              <th scope="col">Jeux</th>
              <th scope="col">Studios</th>
              <th scope="col">Genre de prédilection</th>
              <th scope="col">Studios principaux</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="country in countries" :key="country.iso3">
              <td>{{ country.name }}</td>
              <td class="figure">{{ formatNumber(country.games) }}</td>
              <td class="figure">{{ formatNumber(country.studios) }}</td>
              <td>
                <template v-if="country.favorite_genre">
                  {{ country.favorite_genre }} <span class="figure text-soft">×{{ formatNumber(country.favorite_index ?? 0) }}</span>
                </template>
                <span v-else class="text-soft">Trop peu de jeux</span>
              </td>
              <td class="text-soft">{{ country.top_studios.slice(0, 3).map((studio) => studio.name).join(', ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { CountryValue, StudioCountriesStats } from '~/types'

/** Même seuil que l'API (`MIN_GAMES_FOR_GENRE`). */
const MIN_GAMES = 5

useHead({ title: 'Studios' })

const { data, isLoading, hasError, refresh } = useApiResource<StudioCountriesStats>('/stats/studio-countries/')

const countries = computed(() => data.value?.countries ?? [])
const mapValues = computed<CountryValue[]>(() =>
  countries.value.map((country) => ({ iso3: country.iso3, value: country.games }))
)

function formatGames(value: number): string {
  return `${formatNumber(value)} jeux`
}
</script>
