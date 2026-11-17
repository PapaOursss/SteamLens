<template>
  <div>
    <PageIntro title="Ce qui se vend, et où" is-lab>
      Les ventes par genre dans quatre marchés, en millions d'unités, toutes plateformes confondues.
    </PageIntro>

    <SampleNotice v-if="data?.is_sample" class="mb-2">
      Les ventes Kaggle vgsales ne sont pas encore importées : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <DataBlock
      title="Les quatre marchés"
      note="Choisissez un marché : son poids dans les ventes mondiales et ses genres favoris."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.by_genre.length"
      :height="520"
      @retry="refresh()"
    >
      <RegionalSalesMap :sales="data!.by_genre" />
    </DataBlock>

    <DataBlock
      title="Ventes par genre"
      :note="data?.top_regions.notes"
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!data?.by_genre.length"
      :height="520"
      @retry="refresh()"
    >
      <RegionalSalesChart :sales="data!.by_genre" />
      <details class="mt-6">
        <summary class="link cursor-pointer">Le détail en tableau</summary>
        <div class="overflow-x-auto">
          <table class="data-table mt-2">
            <thead>
              <tr>
                <th scope="col">Genre</th>
                <th scope="col">Amérique du Nord</th>
                <th scope="col">Europe</th>
                <th scope="col">Japon</th>
                <th scope="col">Reste du monde</th>
                <th scope="col">Total mondial</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data!.by_genre" :key="row.genre">
                <td>{{ row.genre }}</td>
                <td class="figure">{{ formatNumber(row.na) }} M</td>
                <td class="figure">{{ formatNumber(row.eu) }} M</td>
                <td class="figure">{{ formatNumber(row.jp) }} M</td>
                <td class="figure">{{ formatNumber(row.other) }} M</td>
                <td class="figure font-semibold">{{ formatNumber(Math.round(worldTotal(row) * 10) / 10) }} M</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { RegionalSalesStats } from '~/types'

useHead({ title: 'Ventes régionales' })

const { data, isLoading, hasError, refresh } = useApiResource<RegionalSalesStats>('/stats/regional-sales/')
</script>
