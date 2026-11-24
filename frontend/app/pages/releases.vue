<template>
  <div>
    <PageIntro title="Calendrier des sorties" is-lab>
      Tout le monde sort-il son jeu le jeudi ? Retrouvez la répartition des dates de sortie par jour de la semaine et par mois, ainsi que le calendrier annuel détaillé façon contributions GitHub.
    </PageIntro>

    <SampleNotice v-if="data?.is_sample" class="mb-6">
      Les jeux datés n'ont pas encore été importés : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <div class="space-y-8">
      <DataBlock
        title="Jour de la semaine × mois de l'année"
        note="Concentration des sorties selon le moment de la semaine et la saison."
        :is-loading="isLoading"
        :has-error="hasError"
        :is-empty="!weekdayMonth.length"
        :height="440"
        @retry="refresh()"
      >
        <ReleaseHeatmapChart :data="weekdayMonth" :days="days" :months="months" :height="380" />
      </DataBlock>

      <DataBlock
        :title="`Calendrier quotidien des sorties (${currentYear})`"
        note="Une case par jour de l'année, de l'absence de sortie aux pics majeurs."
        :is-loading="isLoading"
        :has-error="hasError"
        :is-empty="!dailyContributions.length"
        :height="320"
        @retry="refresh()"
      >
        <template #actions>
          <div v-if="yearOptions.length > 1" class="flex items-center gap-2">
            <SegmentedControl
              :model-value="String(currentYear)"
              :options="yearOptions"
              label="Année"
              @update:model-value="setYear(Number($event))"
            />
          </div>
        </template>

        <ReleaseAnnualCalendar :data="dailyContributions" :year="currentYear" :height="240" />
      </DataBlock>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChoiceOption } from '~/types'

useHead({ title: 'Calendrier des sorties' })

const {
  data,
  selectedYear,
  weekdayMonth,
  dailyContributions,
  days,
  months,
  availableYears,
  setYear,
  isLoading,
  hasError,
  refresh
} = useReleaseCalendar()

const currentYear = computed(() => selectedYear.value ?? 2026)

const yearOptions = computed<ChoiceOption<string>[]>(() => {
  return availableYears.value.map((y) => ({
    value: String(y),
    label: String(y)
  }))
})
</script>
