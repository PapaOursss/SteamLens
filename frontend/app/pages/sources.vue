<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Sources & Méthodologie</h1>
      <p class="text-sm text-slate-400 mt-1">
        Architecture de collecte, fraîcheur des données et choix méthodologiques pour la soutenance.
      </p>
    </header>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Flux de traitement des données</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="step in pipelineSteps" :key="step.step" class="bg-slate-950 border border-slate-800/80 rounded-lg p-4">
          <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-cyan-950 text-cyan-300 border border-cyan-800 mb-2">
            Étape {{ step.step }}
          </span>
          <h3 class="font-bold text-sm text-white mb-1">{{ step.name }}</h3>
          <p class="text-xs text-slate-400 leading-relaxed">{{ step.description }}</p>
        </div>
      </div>
    </section>

    <section class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <h2 class="text-base font-bold text-slate-100">Sources connectées ({{ sources.length }})</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <article v-for="source in sources" :key="source.key" class="bg-slate-950 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-cyan-300 border border-slate-700">
                {{ source.logo }}
              </span>
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-semibold"
                :class="source.last_import?.succeeded ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-slate-800 text-slate-400 border border-slate-700'"
              >
                {{ source.last_import?.succeeded ? 'Opérationnel' : 'En attente' }}
              </span>
            </div>
            <h3 class="font-bold text-sm text-white">{{ source.name }}</h3>
            <p class="text-xs text-slate-400 mt-1 mb-3">{{ source.role }}</p>
          </div>

          <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
            <div class="flex gap-1.5"><strong class="text-slate-300">Licence :</strong> <span>{{ source.license }}</span></div>
            <div class="flex gap-1.5">
              <strong class="text-slate-300">Fraîcheur :</strong>
              <span>{{ source.last_import?.finished_at ? formatDate(source.last_import.finished_at) : "Pas d'import" }}</span>
            </div>
            <div class="flex gap-1.5 text-amber-400/90"><strong class="text-slate-300">Limites :</strong> <span>{{ source.limits }}</span></div>
          </div>
        </article>
      </div>
    </section>

    <section class="bg-amber-950/20 border border-amber-900/40 rounded-xl p-5 space-y-2">
      <h2 class="text-sm font-bold text-amber-300">Limites méthodologiques et éthique</h2>
      <ul class="list-disc list-inside space-y-1 text-xs text-amber-200/80">
        <li v-for="(note, index) in notes" :key="index">{{ note }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

useHead({
  title: 'Sources & Méthodologie — SteamLens'
})

interface ImportRunInfo {
  started_at: string | null
  finished_at: string | null
  rows: number
  succeeded: boolean | null
}

interface SourceInfo {
  key: string
  name: string
  logo: string
  role: string
  license: string
  limits: string
  last_import: ImportRunInfo
}

const pipelineSteps = ref([
  { step: 1, name: 'Collecte', description: 'Imports périodiques avec contrôle de débit et cache local.' },
  { step: 2, name: 'Normalisation', description: 'Schéma unifié pour catalog, pricing, players et geography.' },
  { step: 3, name: 'Agrégation & API', description: 'Séries temporelles et géographiques exposées via DRF.' },
  { step: 4, name: 'Restitution', description: 'Visualisations ECharts interactives et cartographie Nuxt 4.' }
])

const sources = ref<SourceInfo[]>([
  {
    key: 'kaggle_complete',
    name: 'Kaggle — Steam Games Complete',
    logo: 'Kaggle',
    role: 'Base de catalogue, genres, tags et métadonnées initiales.',
    license: 'CC0 Public Domain',
    limits: 'Snapshot figé dans le temps.',
    last_import: { started_at: null, finished_at: null, rows: 0, succeeded: null }
  },
  {
    key: 'steamspy',
    name: 'SteamSpy API',
    logo: 'SteamSpy',
    role: 'Fourchettes de propriétaires et tags communautaires.',
    license: 'Données publiques SteamSpy',
    limits: "Fourchettes estimées avec marge d'incertitude.",
    last_import: { started_at: null, finished_at: null, rows: 0, succeeded: null }
  },
  {
    key: 'steam_web_api',
    name: 'Steam Web API',
    logo: 'Steam',
    role: 'Comptage en temps réel des joueurs connectés (CCU).',
    license: 'Valve Steam API Terms',
    limits: "Pas d'historique direct : constitué par nos snapshots.",
    last_import: { started_at: null, finished_at: null, rows: 0, succeeded: null }
  },
  {
    key: 'frankfurter',
    name: 'Frankfurter API',
    logo: 'BCE',
    role: 'Taux de change officiels pour normalisation monétaire en EUR.',
    license: 'Open Data BCE',
    limits: 'Mise à jour les jours ouvrés bancaires.',
    last_import: { started_at: null, finished_at: null, rows: 0, succeeded: null }
  }
])

const notes = ref<string[]>([
  "Aucune donnée personnelle n'est collectée ni enregistrée (aucun SteamID individuel ou pseudo).",
  'Les distributions régionales sont approchées par les langues ou des sondages publics déclarés.',
  'Toutes les estimations sont étiquetées comme telles pour garantir la rigueur de la soutenance.'
])

function formatDate(isoStr: string): string {
  try {
    return new Date(isoStr).toLocaleString('fr-FR')
  } catch {
    return isoStr
  }
}
</script>
