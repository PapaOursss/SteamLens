export interface TrendsApiResponse {
  timeline: string[]
  series: Record<string, Record<string, number>>
}

export function useTrendsMap(target: { appid?: Ref<number | null>; genre?: Ref<string> }) {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000/api'

  const timeline = ref<string[]>([])
  const series = ref<Record<string, Record<string, number>>>({})
  const currentIndex = ref(0)
  const isPlaying = ref(false)
  const loading = ref(true)
  const error = ref<string | null>(null)

  let timer: ReturnType<typeof setInterval> | null = null

  async function fetchTrends() {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      if (target.appid?.value) {
        params.append('appid', String(target.appid.value))
      }
      if (target.genre?.value) {
        params.append('genre', target.genre.value)
      }

      const res = await $fetch<TrendsApiResponse>(`${apiBase}/stats/trends/?${params.toString()}`)
      timeline.value = res.timeline
      series.value = res.series
      currentIndex.value = 0
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Impossible de charger les données Trends'
    } finally {
      loading.value = false
    }
  }

  const currentDate = computed(() => timeline.value[currentIndex.value] ?? '')
  const currentScores = computed<Record<string, number>>(() => {
    if (!currentDate.value) return {}
    return series.value[currentDate.value] ?? {}
  })

  function togglePlay() {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }

  function play() {
    if (timeline.value.length <= 1) return
    isPlaying.value = true
    timer = setInterval(() => {
      if (currentIndex.value < timeline.value.length - 1) {
        currentIndex.value++
      } else {
        currentIndex.value = 0
      }
    }, 1500)
  }

  function pause() {
    isPlaying.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function setIndex(index: number) {
    pause()
    currentIndex.value = index
  }

  onUnmounted(() => {
    pause()
  })

  return {
    timeline,
    series,
    currentIndex,
    currentDate,
    currentScores,
    isPlaying,
    loading,
    error,
    fetchTrends,
    togglePlay,
    setIndex,
  }
}
