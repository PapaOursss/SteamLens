import type { GameDetail, GameDnaAxis, PlayerCountSnapshotItem, PriceHistory } from '~/types'

export const MAX_COMPARED = 4

export interface ComparedGame {
  game: GameDetail
  dna: GameDnaAxis[]
  players: PlayerCountSnapshotItem[]
  prices: PriceHistory | null
}

/** Les jeux comparés vivent dans l'adresse (`?ids=730,570`) : la page se partage telle quelle. */
export function useComparedGames() {
  const route = useRoute()
  const { get } = useApi()
  const games = ref<ComparedGame[]>([])
  const isLoading = ref(true)
  const missing = ref<number[]>([])
  let latestLoad = 0

  const ids = computed(() => {
    const numbers = String(route.query.ids ?? '').split(',').map(Number)
    return [...new Set(numbers.filter((id) => Number.isInteger(id) && id > 0))].slice(0, MAX_COMPARED)
  })

  function optional<T>(request: Promise<T>, fallback: T): Promise<T> {
    return request.catch(() => fallback)
  }

  async function loadGame(id: number): Promise<ComparedGame | null> {
    try {
      const [game, dna, players, prices] = await Promise.all([
        get<GameDetail>(`/games/${id}/`),
        optional(get<GameDnaAxis[]>(`/games/${id}/dna/`), []),
        optional(get<PlayerCountSnapshotItem[]>(`/games/${id}/players/`), []),
        optional<PriceHistory | null>(get<PriceHistory>(`/stats/price-history/${id}/`), null)
      ])
      return { game, dna, players, prices }
    } catch {
      return null
    }
  }

  async function load() {
    const loadId = ++latestLoad
    const wanted = ids.value
    isLoading.value = true
    const loaded = await Promise.all(wanted.map(loadGame))
    if (loadId !== latestLoad) return
    games.value = loaded.filter((entry) => entry !== null)
    missing.value = wanted.filter((_, index) => loaded[index] === null)
    isLoading.value = false
  }

  function setIds(next: number[]) {
    navigateTo({ query: next.length ? { ids: next.join(',') } : {} })
  }

  function add(id: number) {
    if (!ids.value.includes(id) && ids.value.length < MAX_COMPARED) setIds([...ids.value, id])
  }

  function remove(id: number) {
    setIds(ids.value.filter((other) => other !== id))
  }

  onMounted(load)
  watch(ids, (next, previous) => {
    if (next.join() !== previous.join()) load()
  })

  return { ids, games, missing, isLoading, add, remove, reload: load }
}
