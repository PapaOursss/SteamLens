<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Genres & Tags</h1>
      <p class="text-sm text-slate-400 mt-1">
        Cartographie hiérarchique, treemaps et sunburst des catégories de jeux vidéo.
      </p>
    </header>

    <ChartCard
      title="Treemap des Genres"
      subtitle="Surface = Volume de jeux, Couleur = Popularité estimée"
      source="Kaggle Steam Complete & SteamSpy"
    >
      <div class="flex flex-col items-center justify-center p-8 text-center text-slate-400">
        <p class="text-sm font-medium text-slate-300">Visualisation Treemap & Sunburst</p>
        <p class="text-xs text-slate-400 mt-1 max-w-md">
          Prévue pour la tâche T-15 avec ECharts. Les catégories principales Action, Aventure, RPG et Indé domineront la hiérarchie.
        </p>
      </div>
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Genres & Tags — SteamLens'
})
</script>
