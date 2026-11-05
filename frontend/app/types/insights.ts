export interface PriceChangeRow {
  changed_at: string
  price: number
  regular: number
  cut: number
}

export interface PriceHistory {
  appid: number
  name: string
  currency: string | null
  summary: {
    lowest_price: number | null
    lowest_date: string | null
    promotions: number
    promotions_per_year: number
    average_cut: number
    by_year: { year: number; promotions: number }[]
  }
  changes: PriceChangeRow[]
}

export interface SalesCalendar {
  years: number[]
  cells: [number, number, number][]
}

export interface ReviewWeekRow {
  week_start: string
  positive: number
  negative: number
  positive_share: number
}

export interface ReviewBombing {
  week_start: string
  positive_share: number
  baseline_share: number
  drop: number
  reviews: number
}

export interface GameReviews {
  appid: number
  name: string
  languages: { language: string; positive: number; negative: number; positive_share: number }[]
  weeks: ReviewWeekRow[]
  bombings: ReviewBombing[]
}

export interface BombedGame extends ReviewBombing {
  appid: number
  name: string
}

export interface SurveySeries {
  item: string
  values: (number | null)[]
}

export interface HardwareSurvey {
  category: string
  months: string[]
  series: SurveySeries[]
  highlights: (SurveySeries & { label: string })[]
}

export interface AchievementStep {
  rank: number
  name: string
  percent: number
  is_ending: boolean
}

export interface GameAchievements {
  appid: number
  name: string
  completion_rate: number | null
  biggest_drop: { from_achievement: string; to_achievement: string; drop: number } | null
  curve: AchievementStep[]
}

export interface LeastFinishedGame {
  appid: number
  name: string
  header_image: string
  completion_rate: number
  median_percent: number
  achievements: number
}

export interface ProfileCountries {
  sample: {
    date: string | null
    games: number
    profiles: number
    without_country: number
    without_country_share: number
    unmapped_country: number
  }
  countries: { iso3: string; name: string; profiles: number; share: number }[]
  by_genre: { genre: string; profiles: number; top_country: string; top_country_share: number }[]
}
