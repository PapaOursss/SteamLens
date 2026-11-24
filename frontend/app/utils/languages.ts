/** Les codes de langue de Steam, tels que l'import des avis les demande. */
const LANGUAGE_NAMES: Record<string, string> = {
  all: 'Toutes langues',
  brazilian: 'Portugais (Brésil)',
  english: 'Anglais',
  french: 'Français',
  german: 'Allemand',
  japanese: 'Japonais',
  koreana: 'Coréen',
  polish: 'Polonais',
  russian: 'Russe',
  schinese: 'Chinois simplifié',
  spanish: 'Espagnol',
  turkish: 'Turc'
}

export function languageName(code: string): string {
  return LANGUAGE_NAMES[code] ?? code
}
