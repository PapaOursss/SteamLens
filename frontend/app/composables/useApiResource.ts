import type { MaybeRefOrGetter } from 'vue'

/**
 * Lit une ressource de l'API depuis le navigateur (le serveur Nuxt n'atteint pas toujours le
 * backend, en conteneur par exemple). `isLoading` vaut aussi pour l'attente avant le premier appel.
 */
export function useApiResource<T>(
  endpoint: MaybeRefOrGetter<string>,
  query?: MaybeRefOrGetter<Record<string, string | number | undefined>>
) {
  const config = useRuntimeConfig()
  const url = computed(() => `${config.public.apiBase}${toValue(endpoint)}`)
  const { data, status, refresh } = useFetch<T>(url, {
    query: computed(() => (query ? toValue(query) : {})),
    server: false,
    lazy: true,
    dedupe: 'cancel'
  })

  return {
    data,
    refresh,
    isLoading: computed(() => status.value === 'idle' || status.value === 'pending'),
    hasError: computed(() => status.value === 'error')
  }
}
