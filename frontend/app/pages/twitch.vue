<template>
  <div>
    <PageIntro title="Ce qui se regarde sur Twitch" is-lab>
      Les jeux les plus regardés en ce moment, la langue de ceux qui les diffusent, et la course des jeux regardés depuis 2016.
    </PageIntro>

    <SampleNotice v-if="stats?.is_sample" class="mb-2">
      Le relevé Twitch n'a pas encore tourné : ces chiffres illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <DataBlock
      title="En ce moment"
      :note="takenAtNote"
      :is-loading="statsLoading"
      :has-error="statsError"
      :is-empty="!topRows.length"
      :height="520"
      @retry="refreshStats()"
    >
      <RankBars :rows="topRows" />
    </DataBlock>

    <DataBlock
      title="La langue des streams"
      note="Part des heures regardées sur sept jours, toutes catégories du top confondues. Elle nourrira la carte des genres par pays."
      :is-loading="statsLoading"
      :has-error="statsError"
      :is-empty="!languageRows.length"
      :height="360"
      @retry="refreshStats()"
    >
      <RankBars :rows="languageRows" />
    </DataBlock>

    <SampleNotice v-if="history?.is_sample" class="mb-2">
      L'historique Kaggle n'est pas encore importé : cette course illustre la page, ce ne sont pas des mesures.
    </SampleNotice>

    <DataBlock
      title="La course depuis 2016"
      note="Spectateurs moyens de chaque mois, top 15 (relevés SullyGnome, de janvier 2016 à septembre 2024)."
      :is-loading="historyLoading"
      :has-error="historyError"
      :is-empty="!months.length"
      :height="560"
      @retry="refreshHistory()"
    >
      <div class="space-y-4">
        <div class="flex flex-wrap items-center gap-4">
          <button type="button" class="button" :disabled="months.length < 2" @click="togglePlay">
            {{ isPlaying ? 'Pause' : 'Lecture animée' }}
          </button>
          <label class="flex min-w-48 flex-1 flex-col">
            <span class="text-soft">Mois : <strong class="figure text-text">{{ formatMonth(currentMonth) }}</strong></span>
            <input
              type="range"
              min="0"
              :max="Math.max(0, months.length - 1)"
              :value="currentIndex"
              class="min-h-11 w-full accent-hot"
              @input="setIndex(Number(($event.target as HTMLInputElement).value))"
            >
          </label>
        </div>
        <BarChartRace
          :entries="currentEntries"
          :current-month="currentMonth"
          :height="460"
          label="Course des jeux les plus regardés sur Twitch, mois par mois"
        />
      </div>
    </DataBlock>
  </div>
</template>

<script setup lang="ts">
import type { RankRow, TwitchStats } from '~/types'

useHead({ title: 'Twitch' })

const {
  data: stats,
  isLoading: statsLoading,
  hasError: statsError,
  refresh: refreshStats
} = useApiResource<TwitchStats>('/stats/twitch/')

const {
  data: history,
  isLoading: historyLoading,
  hasError: historyError,
  refresh: refreshHistory,
  months,
  currentIndex,
  currentMonth,
  currentEntries,
  isPlaying,
  togglePlay,
  setIndex
} = usePlayerRace('/stats/twitch-history/')

const languageNames = new Intl.DisplayNames(['fr'], { type: 'language' })

function twitchLanguageName(code: string): string {
  if (code === 'other') return 'Autres langues'
  try {
    const name = languageNames.of(code) ?? code
    return name.charAt(0).toUpperCase() + name.slice(1)
  } catch {
    return code
  }
}

const topRows = computed<RankRow[]>(() =>
  (stats.value?.top ?? []).map((category) => ({
    key: `${category.rank}-${category.name}`,
    label: `${category.rank}. ${category.name}`,
    value: category.viewers,
    display: `${formatCompact(category.viewers)} spectateurs · ${formatNumber(category.streams)} streams`,
    to: category.appid ? gameLink(category.appid) : undefined
  }))
)

const languageRows = computed<RankRow[]>(() =>
  (stats.value?.languages ?? []).map((row) => ({
    key: row.language,
    label: twitchLanguageName(row.language),
    value: row.share,
    display: `${formatNumber(row.share)} %`
  }))
)

const takenAtNote = computed(() => {
  const takenAt = stats.value?.taken_at
  const when = takenAt ? `Relevé du ${formatDateTime(takenAt)}. ` : ''
  return `${when}Un clic mène à la fiche du jeu quand il est sur Steam.`
})
</script>
