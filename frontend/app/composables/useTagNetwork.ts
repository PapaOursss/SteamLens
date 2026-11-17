import type { TagNetworkResponse } from '~/types'

export function useTagNetwork() {
  const { data, isLoading, hasError, refresh } =
    useApiResource<TagNetworkResponse>('/stats/tag-network/')

  const nodes = computed(() => data.value?.nodes ?? [])
  const edges = computed(() => data.value?.edges ?? [])

  return {
    data,
    nodes,
    edges,
    isLoading,
    hasError,
    refresh
  }
}
