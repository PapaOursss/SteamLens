<template>
  <div>
    <PageIntro title="Regardés ou joués ?">
      Les spectateurs Twitch face aux joueurs Steam. Le chiffre à droite donne le nombre de spectateurs par joueur.
    </PageIntro>

    <SampleNotice v-if="isSample" class="mb-6">
      L'import Twitch n'a pas encore tourné : ces lignes illustrent la page, ce ne sont pas des mesures.
    </SampleNotice>

    <div v-if="isLoading" class="mx-4 h-80 animate-pulse bg-deep motion-reduce:animate-none md:mx-6" />
    <div v-else-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Ces données n'arrivent pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="refresh()">Réessayer</button>
    </div>
    <div v-else-if="data" class="gutter grid gap-10 pt-2 lg:grid-cols-2">
      <HypeList
        title="Plus regardés que joués"
        description="Beaucoup de spectateurs pour peu de joueurs."
        :games="data.watched_more"
      />
      <HypeList
        title="Joués en silence"
        description="Des communautés actives que le streaming ignore."
        :games="data.played_in_silence"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HypeStats, SourcesOverviewResponse } from '~/types'

const TWITCH_SOURCE = 'twitch'

useHead({ title: 'Tendances' })

const { data, isLoading, hasError, refresh } = useApiResource<HypeStats>('/stats/hype/')
const { data: sources } = useApiResource<SourcesOverviewResponse>('/sources/')

/** L'API renvoie des lignes d'exemple tant que Twitch n'a rien importé. */
const isSample = computed(() => {
  const twitch = sources.value?.sources.find((source) => source.key === TWITCH_SOURCE)
  return twitch ? !twitch.last_import.succeeded : false
})
</script>
