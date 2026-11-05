<template>
  <div>
    <PageIntro title="Ce qui se vend, et où" is-lab>
      Les ventes par genre dans trois marchés, en millions d'unités, toutes plateformes confondues.
    </PageIntro>

    <SampleNotice class="mb-2">
      L'import des ventes (Kaggle vgsales) n'existe pas encore : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

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
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data!.by_genre" :key="row.genre">
                <td>{{ row.genre }}</td>
                <td class="figure">{{ row.na }} M</td>
                <td class="figure">{{ row.eu }} M</td>
                <td class="figure">{{ row.jp }} M</td>
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
