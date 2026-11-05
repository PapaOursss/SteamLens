import type { Ref } from 'vue'

export interface GameOption {
  appid: number
  name: string
  header_image: string
}

const MINIMUM_QUERY_LENGTH = 2
const SEARCH_DELAY_MS = 300
const RESULT_COUNT = 8

/** Recherche de jeux par nom, lancée quand la frappe se calme ; seule la dernière réponse compte. */
export function useGameSearch(query: Ref<string>) {
  const { get } = useApi()
  const settledQuery = useDebounced(query, SEARCH_DELAY_MS)
  const options = ref<GameOption[]>([])
  const isFetching = ref(false)
  const hasError = ref(false)
  let latestSearch = 0

  watch(settledQuery, async (text) => {
    const searchId = ++latestSearch
    const search = text.trim()
    hasError.value = false
    options.value = []
    isFetching.value = search.length >= MINIMUM_QUERY_LENGTH
    if (!isFetching.value) return
    try {
      const data = await get<{ results: GameOption[] }>('/games/', { search, page_size: RESULT_COUNT })
      if (searchId === latestSearch) options.value = data.results
    } catch {
      if (searchId === latestSearch) hasError.value = true
    } finally {
      if (searchId === latestSearch) isFetching.value = false
    }
  })

  // La frappe en attente compte comme une recherche : pas de « aucun résultat » prématuré.
  const isLoading = computed(() => isFetching.value || query.value !== settledQuery.value)

  return { options, isLoading, hasError }
}
