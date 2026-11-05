/** Appel ponctuel à l'API ; pour une ressource affichée par une page, voir `useApiResource`. */
export function useApi() {
  const config = useRuntimeConfig()

  function get<T>(endpoint: string, query?: Record<string, string | number>): Promise<T> {
    return $fetch<T>(`${config.public.apiBase}${endpoint}`, { query })
  }

  return { get }
}
