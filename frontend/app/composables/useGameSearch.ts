/**
 * Récupère la liste paginée des jeux pour le sélecteur de la carte.
 * Renvoie appid + name, triés par popularité.
 */
export interface GameOption {
  appid: number
  name: string
}

export function useGameSearch(query: Ref<string>) {
  const config = useRuntimeConfig()
  const options = ref<GameOption[]>([])
  const loading = ref(false)

  async function search(q: string) {
    if (q.length < 2) { options.value = []; return }
    loading.value = true
    try {
      const data = await $fetch<{ results: GameOption[] }>(
        `${config.public.apiBase}/games/`,
        { query: { search: q, page_size: 10 } }
      )
      options.value = data.results ?? []
    } catch {
      options.value = []
    } finally {
      loading.value = false
    }
  }

  let timer: ReturnType<typeof setTimeout> | null = null
  watch(query, (q) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => search(q), 300)
  })

  return { options, loading }
}
