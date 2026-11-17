import type { ReleaseCalendarResponse } from '~/types'

export function useReleaseCalendar() {
  const selectedYear = ref<number | null>(null)

  const url = computed(() => {
    return selectedYear.value
      ? `/stats/release-calendar/?year=${selectedYear.value}`
      : '/stats/release-calendar/'
  })

  const { data, isLoading, hasError, refresh } =
    useApiResource<ReleaseCalendarResponse>(url)

  watch(
    () => data.value?.selected_year,
    (newYear) => {
      if (newYear && selectedYear.value === null) {
        selectedYear.value = newYear
      }
    }
  )

  const weekdayMonth = computed(() => data.value?.weekday_month ?? [])
  const dailyContributions = computed(() => data.value?.daily_contributions ?? [])
  const days = computed(() => data.value?.days ?? [])
  const months = computed(() => data.value?.months ?? [])
  const availableYears = computed(() => data.value?.available_years ?? [])

  function setYear(year: number) {
    selectedYear.value = year
  }

  return {
    data,
    selectedYear,
    weekdayMonth,
    dailyContributions,
    days,
    months,
    availableYears,
    setYear,
    isLoading,
    hasError,
    refresh
  }
}
