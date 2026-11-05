export interface RankRow {
  key: string
  label: string
  value: number
  display: string
  to?: string
}

export interface ChoiceOption<T extends string> {
  value: T
  label: string
}

export interface TimePoint {
  date: string
  value: number
}

export interface CountryValue {
  iso3: string
  value: number
}
