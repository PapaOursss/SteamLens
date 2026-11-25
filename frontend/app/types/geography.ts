export interface PurchasingPowerCountry {
  iso3: string
  name: string
  income: number
  year: number
  price_eur: number | null
  hours: number | null
  hours_uniform: number | null
}

export interface PurchasingPower {
  appid: number | null
  name: string | null
  uniform_price_eur: number | null
  has_local_prices: boolean
  countries: PurchasingPowerCountry[]
}

export interface GenreShare {
  genre: string
  share: number
  index: number
}

export interface CountryTaste {
  iso3: string
  name: string
  dominant: string
  reviews: number
  languages: string[]
  genres: GenreShare[]
}

export interface GenresByCountry {
  genres: string[]
  countries: CountryTaste[]
}
