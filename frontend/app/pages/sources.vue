<template>
  <div>
    <PageIntro title="D'où viennent les chiffres">
      Chaque source, ce qu'on en tire, ses limites et son dernier import enregistré.
    </PageIntro>

    <div v-if="isLoading" class="mx-4 h-96 animate-pulse bg-deep motion-reduce:animate-none md:mx-6" />
    <div v-else-if="hasError" class="gutter flex flex-wrap items-center gap-4 bg-deep py-8" role="alert">
      <p>Ces données n'arrivent pas : l'API de SteamLens ne répond pas.</p>
      <button type="button" class="button" @click="refresh()">Réessayer</button>
    </div>
    <template v-else-if="data">
      <section class="gutter py-6">
        <h2 class="mb-4 text-2xl md:text-3xl">Le chemin d'une donnée</h2>
        <ol class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <li v-for="step in data.pipeline.steps" :key="step.step">
            <h3 class="text-xl">{{ step.step }}. {{ step.name }}</h3>
            <p class="mt-1 leading-relaxed text-soft">{{ step.description }}</p>
          </li>
        </ol>
      </section>

      <section class="gutter py-6">
        <h2 class="mb-2 text-2xl md:text-3xl">Les {{ data.sources.length }} sources</h2>
        <ul>
          <li v-for="source in data.sources" :key="source.key" class="grid gap-2 border-t border-line py-4 md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)_minmax(0,2fr)] md:gap-6">
            <div>
              <h3 class="text-lg leading-snug">{{ source.name }}</h3>
              <p class="text-soft">{{ source.license }}</p>
            </div>
            <p class="max-w-prose leading-relaxed text-soft">{{ source.role }} {{ source.limits }}</p>
            <p :class="statusOf(source).isStrong ? 'font-semibold' : 'text-soft'">{{ statusOf(source).text }}</p>
          </li>
        </ul>
      </section>

      <section class="gutter py-6">
        <h2 class="mb-3 text-2xl md:text-3xl">Les limites</h2>
        <ul class="max-w-prose list-disc space-y-2 pl-5 leading-relaxed text-soft">
          <li v-for="note in data.methodology_notes" :key="note">{{ note }}</li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SourceInfo, SourcesOverviewResponse } from '~/types'

useHead({ title: 'Sources et méthode' })

const { data, isLoading, hasError, refresh } = useApiResource<SourcesOverviewResponse>('/sources/')

function statusOf(source: SourceInfo): { text: string; isStrong: boolean } {
  const { succeeded, finished_at: finishedAt, rows } = source.last_import
  if (succeeded === false) return { text: 'Dernier import en échec', isStrong: true }
  if (succeeded && finishedAt) {
    return { text: `Importée le ${formatDateTime(finishedAt)}, ${formatNumber(rows)} lignes`, isStrong: true }
  }
  return { text: 'Aucun import enregistré sur cette base', isStrong: false }
}
</script>
