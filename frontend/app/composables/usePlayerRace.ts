export interface RaceGameEntry {
  /** null : pas sur Steam (catégories Twitch comme « Just Chatting »). */
  appid: number | null
  name: string
  players: number
}

export interface MonthlyRaceResponse {
  is_sample: boolean
  months: string[]
  timeline: Record<string, RaceGameEntry[]>
}

/** Autant de jeux suivis que de couleurs de séries : au-delà, ils restent neutres. */
const TRACKED_GAMES = 8
const PODIUM_SIZE = 5

/**
 * Les jeux le plus souvent dans le top 5 d'un mois, du plus fidèle au moins fidèle : chacun
 * garde sa couleur (`seriesColor(rang)`) d'un graphique de la course à l'autre.
 */
export function trackedRaceGames(months: string[], timeline: Record<string, RaceGameEntry[]>): string[] {
  const appearances = new Map<string, number>()
  for (const month of months) {
    for (const entry of (timeline[month] ?? []).slice(0, PODIUM_SIZE)) {
      appearances.set(entry.name, (appearances.get(entry.name) ?? 0) + 1)
    }
  }
  return [...appearances]
    .sort((first, second) => second[1] - first[1])
    .slice(0, TRACKED_GAMES)
    .map(([name]) => name)
}

/** Course mois par mois ; `path` change la mesure (joueurs Steam, spectateurs Twitch…). */
export function usePlayerRace(path = '/stats/monthly-player-race/') {
  const { data, isLoading, hasError, refresh } = useApiResource<MonthlyRaceResponse>(path)

  const currentIndex = ref(0)
  const isPlaying = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  const months = computed(() => data.value?.months ?? [])
  const currentMonth = computed(() => months.value[currentIndex.value] ?? '')
  const currentEntries = computed<RaceGameEntry[]>(() => {
    if (!currentMonth.value || !data.value?.timeline) return []
    return data.value.timeline[currentMonth.value] ?? []
  })

  function togglePlay() {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }

  function play() {
    if (months.value.length <= 1) return
    isPlaying.value = true
    timer = setInterval(() => {
      if (currentIndex.value < months.value.length - 1) {
        currentIndex.value++
      } else {
        currentIndex.value = 0
      }
    }, 1200)
  }

  function pause() {
    isPlaying.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function setIndex(idx: number) {
    pause()
    currentIndex.value = Math.max(0, Math.min(idx, months.value.length - 1))
  }

  onUnmounted(() => {
    pause()
  })

  return {
    data,
    isLoading,
    hasError,
    refresh,
    months,
    currentIndex,
    currentMonth,
    currentEntries,
    isPlaying,
    togglePlay,
    setIndex,
  }
}
