import type { Ref } from 'vue'

export interface RaceGameEntry {
  appid: number
  name: string
  players: number
}

export interface MonthlyRaceResponse {
  months: string[]
  timeline: Record<string, RaceGameEntry[]>
}

export function usePlayerRace() {
  const { data, isLoading, hasError, refresh } = useApiResource<MonthlyRaceResponse>('/stats/monthly-player-race/')

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
