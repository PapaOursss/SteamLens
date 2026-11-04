<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Cartographie Mondiale</h1>
      <p class="text-sm text-slate-400 mt-1">
        Visualisation géographique des prix régionaux et de la fréquentation par pays.
      </p>
    </header>

    <ChartCard
      title="Carte Choroplèthe Mondiale"
      subtitle="Disparités de prix et pouvoir d'achat par territoire"
      source="Steam Store API & BCE Frankfurter"
    >
      <div class="flex flex-col items-center justify-center p-8 text-center text-slate-400">
        <p class="text-sm font-medium text-slate-300">Carte du Monde Interactive ECharts</p>
        <p class="text-xs text-slate-400 mt-1 max-w-md">
          Prévue pour la tâche T-16. L'endpoint DRF <code class="text-cyan-400 font-mono">/api/map/&lt;indicator&gt;/</code> alimentera les contours GeoJSON des pays.
        </p>
      </div>
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Cartographie Mondiale — SteamLens'
})
</script>
