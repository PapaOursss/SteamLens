<template>
  <div class="sources-page">
    <header class="page-header">
      <h1 class="title">Sources & Méthodologie</h1>
      <p class="subtitle">
        Architecture de collecte, fraîcheur des données et choix méthodologiques pour la soutenance.
      </p>
    </header>

    <section class="section">
      <h2 class="section-title">Flux de traitement des données</h2>
      <div class="pipeline-grid">
        <div v-for="step in pipelineSteps" :key="step.step" class="step-card">
          <div class="step-badge">Étape {{ step.step }}</div>
          <h3 class="step-name">{{ step.name }}</h3>
          <p class="step-description">{{ step.description }}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Sources connectées ({{ sources.length }})</h2>
      <div class="sources-grid">
        <article v-for="source in sources" :key="source.key" class="source-card">
          <div class="source-header">
            <span class="source-tag">{{ source.logo }}</span>
            <span class="status-pill" :class="source.last_import?.succeeded ? 'pill-success' : 'pill-idle'">
              {{ source.last_import?.succeeded ? 'Opérationnel' : 'En attente' }}
            </span>
          </div>
          <h3 class="source-name">{{ source.name }}</h3>
          <p class="source-role">{{ source.role }}</p>
          <div class="source-meta">
            <div class="meta-row"><strong>Licence :</strong> <span>{{ source.license }}</span></div>
            <div class="meta-row">
              <strong>Fraîcheur :</strong>
              <span>{{ source.last_import?.finished_at ? formatDate(source.last_import.finished_at) : 'Pas d\'import' }}</span>
            </div>
            <div class="meta-row limits-row"><strong>Limites :</strong> <span>{{ source.limits }}</span></div>
          </div>
        </article>
      </div>
    </section>

    <section class="section notes-section">
      <h2 class="section-title">Limites méthodologiques et éthique</h2>
      <ul class="notes-list">
        <li v-for="(note, index) in notes" :key="index">{{ note }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

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
    limits: 'Fourchettes estimées avec marge d\'incertitude.',
    last_import: { started_at: null, finished_at: null, rows: 0, succeeded: null }
  },
  {
    key: 'steam_web_api',
    name: 'Steam Web API',
    logo: 'Steam',
    role: 'Comptage en temps réel des joueurs connectés (CCU).',
    license: 'Valve Steam API Terms',
    limits: 'Pas d\'historique direct : constitué par nos snapshots.',
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
  'Aucune donnée personnelle n\'est collectée ni enregistrée (aucun SteamID individuel ou pseudo).',
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

<style scoped>
.sources-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1f2937;
}
.page-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}
.title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
}
.subtitle {
  color: #4b5563;
  margin: 0;
}
.section {
  margin-bottom: 2.5rem;
}
.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
}
.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.step-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}
.step-badge {
  display: inline-block;
  background: #2563eb;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  margin-bottom: 0.4rem;
}
.step-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.4rem 0;
}
.step-description {
  font-size: 0.85rem;
  color: #4b5563;
  margin: 0;
}
.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.source-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.source-tag {
  background: #e0e7ff;
  color: #3730a3;
  font-weight: 600;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
}
.status-pill {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.4rem;
  border-radius: 9999px;
}
.pill-success { background: #dcfce7; color: #166534; }
.pill-idle { background: #f3f4f6; color: #6b7280; }
.source-name {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.4rem 0;
}
.source-role {
  font-size: 0.85rem;
  color: #374151;
  margin: 0 0 0.8rem 0;
}
.source-meta {
  font-size: 0.8rem;
  color: #4b5563;
  border-top: 1px dashed #e5e7eb;
  padding-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.meta-row { display: flex; gap: 0.3rem; }
.limits-row { color: #9a3412; }
.notes-section {
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 0.5rem;
  padding: 1.25rem;
}
.notes-list {
  margin: 0;
  padding-left: 1.2rem;
  color: #92400e;
  line-height: 1.5;
  font-size: 0.9rem;
}
</style>
