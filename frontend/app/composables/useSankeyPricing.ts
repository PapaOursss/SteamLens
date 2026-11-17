import type { SankeyPriceReviewResponse } from '~/types'

export function useSankeyPricing() {
  const { data, isLoading, hasError, refresh } =
    useApiResource<SankeyPriceReviewResponse>('/stats/sankey-pricing/')

  const nodes = computed(() => data.value?.nodes ?? [])
  const links = computed(() => data.value?.links ?? [])
  const genres = computed(() => data.value?.genres ?? [])

  return {
    data,
    nodes,
    links,
    genres,
    isLoading,
    hasError,
    refresh
  }
}
