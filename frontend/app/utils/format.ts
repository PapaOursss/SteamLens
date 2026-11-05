const NUMBER_FORMAT = new Intl.NumberFormat('fr-FR')
const COMPACT_FORMAT = new Intl.NumberFormat('fr-FR', { notation: 'compact', maximumFractionDigits: 1 })
const PRICE_FORMAT = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' })
const DATE_TIME_FORMAT = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long', timeStyle: 'short' })
const DATE_FORMAT = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long' })

/** L'espace fine de `fr-FR` disparaît presque dans notre police : espace insécable à la place. */
function widenSpaces(text: string): string {
  return text.replaceAll(' ', ' ')
}

export function formatNumber(value: number): string {
  return widenSpaces(NUMBER_FORMAT.format(value))
}

export function formatCompact(value: number): string {
  return widenSpaces(COMPACT_FORMAT.format(value))
}

export function formatPrice(value: number): string {
  return widenSpaces(PRICE_FORMAT.format(value))
}

export function formatDateTime(isoDate: string): string {
  return DATE_TIME_FORMAT.format(new Date(isoDate))
}

export function formatDate(isoDate: string): string {
  return DATE_FORMAT.format(new Date(isoDate))
}
