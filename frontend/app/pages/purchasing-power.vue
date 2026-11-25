<template>
  <div>
    <PageIntro title="Combien d'heures pour un jeu ?" is-lab>
      <template #under-title>
        <GameSearch field-id="recherche-pouvoir-achat" label="Un autre jeu" class="mt-5 max-w-md" @select="selectGame" />
      </template>
      Le prix d'un jeu rapporté au revenu de chaque pays : PIB par habitant en parité de pouvoir d'achat, divisé par
      2 080 heures de travail par an. Un ordre de grandeur, pas un salaire.
    </PageIntro>

    <DataBlock
      :title="title"
      note="Boutique Steam (prix convertis en euros), Banque mondiale."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!values.length"
      :empty-message="emptyMessage"
      :height="560"
      @retry="refresh()"
    >
      <template #actions>
        <SegmentedControl v-if="data?.has_local_prices" v-model="mode" :options="MODES" label="Prix retenu" />
      </template>
      <WorldValueMap :values="values" :scale="scale" :format-value="formatHours" :label="title" />
      <div class="mt-8 grid gap-8 md:grid-cols-2">
        <div>
          <h3 class="mb-3 text-xl">Là où il coûte le plus d'heures</h3>
          <RankBars :rows="rows.slice(0, LIST_LENGTH)" :maximum="rows[0]?.value" />
        </div>
        <div>
          <h3 class="mb-3 text-xl">Là où il en coûte le moins</h3>
          <RankBars :rows="rows.slice(-LIST_LENGTH).reverse()" :maximum="rows[0]?.value" />
        </div>
      </div>
    </DataBlock>

    <DataBlock
      v-if="effects.length"
      title="L'effet des prix régionaux"
      note="Avant : le prix américain appliqué partout. Après : le prix local de Steam."
    >
      <div class="overflow-x-auto">
        <table class="data-table max-w-3xl">
          <thead>
            <tr>
              <th scope="col">Pays</th>
              <th scope="col">Avant</th>
              <th scope="col">Après</th>
              <th scope="col">Écart</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="effect in effects" :key="effect.iso3">
              <td>{{ effect.name }}</td>
              <td class="figure">{{ formatHours(effect.before) }}</td>
              <td class="figure">{{ formatHours(effect.after) }}</td>
              <td class="figure">{{ effect.change > 0 ? '+' : '' }}{{ formatPercent(effect.change) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption, PurchasingPower, RankRow } from '~/types'

type Mode = 'local' | 'uniform'

const LIST_LENGTH = 8
const PERCENT = 100
const MODES: ChoiceOption<Mode>[] = [
  { value: 'local', label: 'Prix local' },
  { value: 'uniform', label: 'Prix américain partout' }
]

useHead({ title: "Pouvoir d'achat" })

const { appid, selectGame } = useGameFromRoute()
const { data, isLoading, hasError, refresh } = useApiResource<PurchasingPower>(
  () => `/stats/purchasing-power/?appid=${appid.value}`
)
const mode = ref<Mode>('local')
const isLocal = computed(() => mode.value === 'local' && Boolean(data.value?.has_local_prices))

const values = computed(() =>
  (data.value?.countries ?? []).flatMap((country) => {
    const value = isLocal.value ? country.hours : country.hours_uniform
    return value === null ? [] : [{ iso3: country.iso3, value }]
  })
)

/** Même échelle dans les deux modes : la bascule montre l'écart. */
const scale = computed(() => {
  const all = (data.value?.countries ?? []).flatMap((c) => [c.hours, c.hours_uniform]).filter((v) => v !== null)
  return { min: Math.min(...all), max: Math.max(...all) }
})

const title = computed(() => {
  if (data.value?.has_local_prices) return `Heures de travail pour ${data.value.name}`
  return 'Heures de travail pour un jeu à 60 €'
})

const emptyMessage = computed(() =>
  data.value?.countries.length
    ? "Ce jeu n'a pas de prix américain relevé."
    : "Pas encore de revenus : l'import de la Banque mondiale n'a pas tourné sur cette base."
)

const rows = computed<RankRow[]>(() =>
  [...values.value]
    .sort((first, second) => second.value - first.value)
    .map(({ iso3, value }) => ({ key: iso3, label: countryName(iso3), value, display: formatHours(value) }))
)

const effects = computed(() =>
  (data.value?.countries ?? [])
    .flatMap(({ iso3, name, hours, hours_uniform: uniform }) =>
      hours === null || !uniform
        ? []
        : [{ iso3, name, before: uniform, after: hours, change: Math.round((hours / uniform - 1) * PERCENT) }]
    )
    .sort((first, second) => first.change - second.change)
)

function formatHours(hours: number): string {
  return `${formatNumber(Math.round(hours * 10) / 10)} h`
}
</script>
