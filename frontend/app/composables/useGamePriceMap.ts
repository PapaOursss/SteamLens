/**
 * Récupère les prix du dernier relevé pour un jeu donné, par pays (iso3 → price_eur).
 * Données issues de /api/games/<appid>/prices/.
 */
export interface CountryPrice {
  iso3: string
  price_eur: number
  currency: string
  price: number
}

export function useGamePriceMap(appid: Ref<number | null>) {
  const config = useRuntimeConfig()
  const prices = ref<CountryPrice[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPrices(id: number) {
    loading.value = true
    error.value = null
    try {
      const raw = await $fetch<RawPricePoint[]>(
        `${config.public.apiBase}/games/${id}/prices/`
      )
      prices.value = latestByCountry(raw)
    } catch {
      error.value = 'Impossible de charger les prix.'
      prices.value = []
    } finally {
      loading.value = false
    }
  }

  watch(appid, (id) => { if (id) fetchPrices(id) }, { immediate: true })

  return { prices, loading, error }
}

interface RawPricePoint {
  date: string
  country: string   // iso2
  currency: string
  price: string
  price_eur: string | null
  discount_percent: number
}

/** Garde uniquement le point le plus récent par pays. */
function latestByCountry(points: RawPricePoint[]): CountryPrice[] {
  const best = new Map<string, RawPricePoint>()
  for (const p of points) {
    const existing = best.get(p.country)
    if (!existing || p.date > existing.date) best.set(p.country, p)
  }
  const result: CountryPrice[] = []
  for (const p of best.values()) {
    if (p.price_eur === null) continue
    result.push({
      iso3: p.country,
      price_eur: parseFloat(p.price_eur),
      currency: p.currency,
      price: parseFloat(p.price),
    })
  }
  return result
}
