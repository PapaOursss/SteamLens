<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Catalogue des Jeux</h1>
      <p class="text-sm text-slate-400 mt-1">
        Recherche multicritère, fiches détaillées et métadonnées issues du catalogue Steam.
      </p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-4">
        <ChartCard
          title="Jeux les plus populaires"
          subtitle="Titres avec le plus grand nombre de joueurs actifs"
          source="Steam Web API"
        >
          <div class="p-6 text-center text-slate-400">
            <p class="text-sm">Consultez les fiches détaillées des jeux suivis par l'observatoire.</p>
            <p class="text-xs text-slate-400 mt-2">Module en cours de développement (T-14 · Fiche jeu complète).</p>
          </div>
        </ChartCard>
      </div>

      <div>
        <ChartCard
          title="Filtres rapides"
          subtitle="Recherche par tag ou studio"
          source="Catalogue unifié"
        >
          <div class="p-4 space-y-3 text-xs text-slate-300">
            <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
              🎮 Plus de 100 000 jeux référencés
            </div>
            <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
              🏷️ Tags SteamSpy et IGDB associés
            </div>
            <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
              🏷️ Détection de compatibilité Proton
            </div>
          </div>
        </ChartCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Catalogue des Jeux — SteamLens'
})
</script>
