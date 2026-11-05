<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Analyse des Prix & Soldes</h1>
      <p class="text-sm text-slate-400 mt-1">
        Évolution historique des tarifs, rabais Steam, seuils les plus bas et comparaison internationale.
      </p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <ChartCard
        title="Historique des Prix"
        subtitle="Suivi des prix de vente et périodes de soldes"
        source="IsThereAnyDeal & CheapShark"
      >
        <div class="flex flex-col items-center justify-center p-8 text-center text-slate-400">
          <p class="text-sm font-medium text-slate-300">Courbe temporelle de prix</p>
          <p class="text-xs text-slate-400 mt-1">
            Intégration prévue pour la tâche T-18 avec alertes de prix historiquement bas.
          </p>
        </div>
      </ChartCard>

      <ChartCard
        title="Comparatif Multidevises"
        subtitle="Prix convertis en EUR selon les cours de la BCE"
        source="Frankfurter API"
      >
        <div class="flex flex-col items-center justify-center p-8 text-center text-slate-400">
          <p class="text-sm font-medium text-slate-300">Indice de parité régionale</p>
          <p class="text-xs text-slate-400 mt-1">
            Permet de comparer les variations de prix d'un jeu entre l'Europe, les USA, l'Argentine et la Turquie.
          </p>
        </div>
      </ChartCard>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Analyse des Prix — SteamLens'
})
</script>
