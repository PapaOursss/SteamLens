const TOOLTIP_PADDING = 10

function prefersReducedMotion(): boolean {
  return import.meta.client && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** Réglages communs à tous les graphiques ECharts du site. */
export function chartBase() {
  return {
    animation: !prefersReducedMotion(),
    textStyle: { fontFamily: FONT_BODY, color: COLORS.soft },
    tooltip: {
      backgroundColor: COLORS.deep,
      borderColor: COLORS.line,
      padding: TOOLTIP_PADDING,
      textStyle: { color: COLORS.text, fontFamily: FONT_BODY }
    }
  }
}

export function axisStyle() {
  return {
    axisLine: { lineStyle: { color: COLORS.line } },
    axisTick: { show: false },
    axisLabel: { color: COLORS.soft },
    splitLine: { lineStyle: { color: COLORS.raised } }
  }
}

/** Échappe un texte venu de l'API avant de le mettre dans une infobulle ECharts (HTML). */
export function escapeHtml(text: string): string {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}
