/** Thème choisi, gardé d'une visite à l'autre ; sombre par défaut. */
export function useTheme() {
  const theme = useState<ThemeName>('theme', () => DEFAULT_THEME)

  function setTheme(next: ThemeName) {
    theme.value = next
    applyPalette(next)
    document.documentElement.dataset.theme = next
  }

  function toggle() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme.value)
    } catch {
      // Stockage refusé par le navigateur : le choix vaut pour cette visite.
    }
  }

  /** Après l'hydratation : le serveur ne connaît pas le choix enregistré. */
  function restore() {
    if (document.documentElement.dataset.theme === 'light') setTheme('light')
  }

  return { theme, toggle, restore }
}
