<template>
  <div class="space-y-6">
    <header class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white tracking-tight">Carte n°6 : pays déclarés des profils</h1>
      <p class="text-sm text-slate-400 mt-1">
        Pays affiché (facultatif) sur les profils publics des auteurs d'avis récents. Aucun SteamID
        ni pseudo n'est enregistré : seulement des comptes par pays.
      </p>
    </header>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatTile label="Profils lus" :value="sample?.profiles ?? 0" :hint="sample?.date ?? undefined" />
      <StatTile label="Jeux échantillonnés" :value="sample?.games ?? 0" />
      <StatTile
        label="Sans pays déclaré"
        :value="`${Math.round((sample?.without_country_share ?? 0) * PERCENT)} %`"
        :hint="`${sample?.without_country ?? 0} profils`"
      />
      <StatTile label="Pays hors carte" :value="sample?.unmapped_country ?? 0" hint="pays absents de la table" />
    </div>

    <ChartCard
      title="Profils par pays déclaré"
      :subtitle="`Échantillon : ${sample?.profiles ?? 0} profils publics`"
      source="Steam Web API (GetPlayerSummaries)"
      :loading="loading"
      :empty="!Object.keys(mapValues).length"
      empty-message="Aucun échantillon : lancer manage.py import_profile_countries (clé STEAM_API_KEY)."
      height="440px"
    >
      <CountryValueMap :values="mapValues" unit="profils" />
    </ChartCard>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <ChartCard title="Pays les plus représentés" source="Steam Web API" :empty="!data?.countries.length" height="200px">
        <ul class="w-full divide-y divide-slate-800/60 text-sm">
          <li v-for="country in data?.countries ?? []" :key="country.iso3" class="flex justify-between py-1.5">
            <span class="text-slate-100">{{ country.name }}</span>
            <span class="text-slate-400">{{ country.profiles }} · {{ Math.round(country.share * PERCENT) }} %</span>
          </li>
        </ul>
      </ChartCard>
      <ChartCard title="Pays dominant par genre" source="Steam Web API" :empty="!data?.by_genre.length" height="200px">
        <ul class="w-full divide-y divide-slate-800/60 text-sm">
          <li v-for="row in data?.by_genre ?? []" :key="row.genre" class="flex justify-between py-1.5">
            <span class="text-slate-100">{{ row.genre }}</span>
            <span class="text-slate-400">
              {{ row.top_country }} · {{ Math.round(row.top_country_share * PERCENT) }} % de {{ row.profiles }}
            </span>
          </li>
        </ul>
      </ChartCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProfileCountries } from '~/types'

useHead({ title: 'Pays des profils — SteamLens' })

const PERCENT = 100
const { get } = useApi()
const data = ref<ProfileCountries | null>(null)
const mapValues = ref<Record<string, number>>({})
const loading = ref(true)

const sample = computed(() => data.value?.sample)

onMounted(async () => {
  try {
    const [stats, values] = await Promise.all([
      get<ProfileCountries>('/stats/profile-countries/'),
      get<Record<string, number>>('/map/profile-countries/')
    ])
    data.value = stats
    mapValues.value = values
  } finally {
    loading.value = false
  }
})
</script>
