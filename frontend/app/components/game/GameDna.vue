<template>
  <DataBlock
    title="L'ADN du jeu"
    note="Chaque axe range le jeu de 0 (le plus bas) à 100 (le plus haut) parmi les jeux suivis qui ont cette donnée."
    :is-loading="isLoading"
    :has-error="hasError"
    :is-empty="!hasScore"
    empty-message="Pas encore assez de données pour dessiner l'ADN de ce jeu."
    :height="RADAR_HEIGHT"
    @retry="refresh()"
  >
    <div class="grid items-center gap-6 md:grid-cols-[3fr_2fr]">
      <RadarScoreChart :axes="axes" :height="RADAR_HEIGHT" :label="`Radar de l'ADN de ${name}`" />
      <table class="data-table">
        <thead>
          <tr>
            <th scope="col">Axe</th>
            <th scope="col">Rang</th>
            <th scope="col">Mesure</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="axis in axes" :key="axis.label">
            <td>{{ axis.label }}</td>
            <td class="figure">{{ axis.score ?? '—' }}</td>
            <td>{{ axis.detail }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </DataBlock>
</template>

<script setup lang="ts">
import type { GameDnaAxis, GameDnaKey, RadarAxis } from '~/types'

const RADAR_HEIGHT = 360
const MINUTES_PER_HOUR = 60
const PERCENT = 100

const props = defineProps<{ appid: number; name: string }>()

const { data, isLoading, hasError, refresh } = useApiResource<GameDnaAxis[]>(() => `/games/${props.appid}/dna/`)

/** Libellé de l'axe et phrase qui dit sa mesure brute. */
const AXES: Record<GameDnaKey, { label: string; describe: (raw: number) => string }> = {
  rating: { label: 'Note', describe: (raw) => `${Math.round(raw)} % d'avis positifs` },
  popularity: { label: 'Popularité', describe: (raw) => `${formatCompact(raw)} propriétaires estimés` },
  price: { label: 'Prix', describe: (raw) => (raw ? `${formatPrice(raw)} en France` : 'Gratuit') },
  lifespan: {
    label: 'Durée de vie',
    describe: (raw) => `${formatNumber(Math.round(raw / MINUTES_PER_HOUR))} h de jeu médianes`
  },
  twitch: { label: 'Buzz Twitch', describe: (raw) => `${formatNumber(raw)} spectateurs au dernier relevé` },
  achievement_rarity: {
    label: 'Rareté des succès',
    describe: (raw) => `succès débloqué par ${Math.round(PERCENT - raw)} % des joueurs en moyenne`
  }
}

const axes = computed<RadarAxis[]>(() =>
  (data.value ?? []).map(({ key, score, raw }) => ({
    label: AXES[key].label,
    score,
    detail: raw === null ? 'Pas de donnée' : AXES[key].describe(raw)
  }))
)

const hasScore = computed(() => axes.value.some((axis) => axis.score !== null))
</script>
