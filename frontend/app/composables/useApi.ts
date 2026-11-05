export function useApi() {
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000/api'

  function buildUrl(endpoint: string): string {
    const cleanBase = apiBase.replace(/\/+$/, '')
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    return `${cleanBase}${cleanEndpoint}`
  }

  function get<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
    return $fetch<T>(buildUrl(endpoint), {
      method: 'GET',
      query: params
    })
  }

  function post<T>(endpoint: string, body?: unknown): Promise<T> {
    return $fetch<T>(buildUrl(endpoint), {
      method: 'POST',
      body
    })
  }

  return {
    apiBase,
    buildUrl,
    get,
    post
  }
}
