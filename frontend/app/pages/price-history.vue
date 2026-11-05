<template>
  <div>
    <PageIntro title="Historique des prix et soldes" is-lab>
      Chaque changement de prix sur Steam depuis des années, et les soldes d'été et d'hiver qui reviennent.
    </PageIntro>

    <DataBlock
      title="Calendrier des soldes"
      note="Jeux qui passent en promo, par année et semaine. Source : IsThereAnyDeal."
      :is-loading="calendarLoading"
      :has-error="calendarError"
      :is-empty="!calendar?.cells.length"
      empty-message="Pas encore de données : l'import IsThereAnyDeal n'a pas tourné sur cette base."
      @retry="refreshCalendar()"
    >
      <SalesCalendarChart v-if="calendar" :calendar="calendar" />
    </DataBlock>

    <DataBlock
      :title="history?.name ?? 'Un jeu'"
      note="Prix sur Steam en France, et prix hors promo."
      :is-loading="isLoading"
      :has-error="hasError"
      :is-empty="!history?.changes.length"
      empty-message="Pas encore d'historique pour ce jeu."
      :height="320"
      @retry="refresh()"
    >
      <template #actions>
        <GameSearch field-id="recherche-historique" label="Un autre jeu" class="w-full sm:w-80" @select="selectGame" />
      </template>
      <template v-if="history">
        <div class="mb-6 grid grid-cols-2 gap-x-8 gap-y-4 lg:grid-cols-4">
          <StatTile label="Plus bas historique" :value="lowest" :hint="lowestDate" />
          <StatTile label="Promos" :value="formatNumber(history.summary.promotions)" />
          <StatTile label="Promos par an" :value="formatNumber(history.summary.promotions_per_year)" />
          <StatTile label="Remise moyenne" :value="formatPercent(history.summary.average_cut)" />
        </div>
        <PriceStepChart :changes="history.changes" :currency="history.currency" :label="`Prix de ${history.name} au fil du temps`" />
      </template>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { PriceHistory, SalesCalendar } from '~/types'

useHead({ title: 'Historique des prix' })

const { appid, selectGame } = useGameFromRoute()

const {
  data: calendar,
  isLoading: calendarLoading,
  hasError: calendarError,
  refresh: refreshCalendar
} = useApiResource<SalesCalendar>('/stats/sales-calendar/')
const { data: history, isLoading, hasError, refresh } = useApiResource<PriceHistory>(() => `/stats/price-history/${appid.value}/`)

const lowest = computed(() => {
  const price = history.value?.summary.lowest_price
  return price ? formatAmount(price, history.value?.currency ?? null) : '—'
})
const lowestDate = computed(() => {
  const date = history.value?.summary.lowest_date
  return date ? formatDate(date) : undefined
})
</script>
