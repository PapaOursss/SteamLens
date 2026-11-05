/** Pays servis par l'API : les prix parlent en ISO2, les contours de la carte en ISO3. */
const ISO2_TO_ISO3: Record<string, string> = {
  AE: 'ARE', AR: 'ARG', AU: 'AUS', BR: 'BRA', CA: 'CAN', CH: 'CHE', CL: 'CHL', CN: 'CHN',
  CO: 'COL', CZ: 'CZE', DE: 'DEU', DK: 'DNK', ES: 'ESP', FR: 'FRA', GB: 'GBR', HK: 'HKG',
  HU: 'HUN', ID: 'IDN', IL: 'ISR', IN: 'IND', IT: 'ITA', JP: 'JPN', KR: 'KOR', KW: 'KWT',
  KZ: 'KAZ', MX: 'MEX', MY: 'MYS', NO: 'NOR', NZ: 'NZL', PE: 'PER', PH: 'PHL', PL: 'POL',
  QA: 'QAT', RO: 'ROU', RU: 'RUS', SA: 'SAU', SE: 'SWE', SG: 'SGP', TH: 'THA', TR: 'TUR',
  TW: 'TWN', UA: 'UKR', US: 'USA', UY: 'URY', VN: 'VNM', ZA: 'ZAF'
}

const ISO3_TO_ISO2 = Object.fromEntries(
  Object.entries(ISO2_TO_ISO3).map(([iso2, iso3]) => [iso3, iso2])
)

const COUNTRY_NAMES = new Intl.DisplayNames(['fr'], { type: 'region' })

export function toIso3(iso2: string): string {
  return ISO2_TO_ISO3[iso2] ?? iso2
}

/** Nom français du pays ; le code tel quel si on ne le connaît pas. */
export function countryName(iso3: string): string {
  const iso2 = ISO3_TO_ISO2[iso3]
  return iso2 ? (COUNTRY_NAMES.of(iso2) ?? iso3) : iso3
}
