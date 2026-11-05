import type { Ref } from 'vue'
import type { PricePointItem } from '~/types'

export interface CountryPrice {
  iso3: string
  price_eur: number
  discount_percent: number
}

/** Le relevé le plus récent de chaque pays ayant un prix en euros. */
function latestByCountry(points: PricePointItem[]): CountryPrice[] {
  const latest = new Map<string, PricePointItem>()
  for (const point of points) {
    const known = latest.get(point.country)
    if (!known || point.date > known.date) latest.set(point.country, point)
  }
  return [...latest.values()]
    .filter((point) => point.price_eur !== null)
    .map((point) => ({
      iso3: toIso3(point.country),
      price_eur: Number(point.price_eur),
      discount_percent: point.discount_percent
    }))
}

/** Prix d'un jeu : dernier relevé par pays, et tous les relevés pour la courbe. */
export function useGamePriceMap(appid: Ref<number>) {
  const { data, isLoading, hasError, refresh } = useApiResource<PricePointItem[]>(
    () => `/games/${appid.value}/prices/`
  )

  return {
    isLoading,
    hasError,
    refresh,
    points: computed(() => data.value ?? []),
    prices: computed(() => latestByCountry(data.value ?? []))
  }
}
