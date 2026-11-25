/** Thème ECharts commun : ce qu'un graphique ne règle pas lui-même vient d'ici. */
export function chartTheme() {
  const axis = { ...axisStyle(), nameTextStyle: { color: COLORS.soft } }
  return {
    color: [...SERIES_COLORS],
    backgroundColor: 'transparent',
    ...chartBase(),
    legend: { textStyle: { color: COLORS.text }, inactiveColor: COLORS.line },
    categoryAxis: axis,
    valueAxis: axis,
    timeAxis: axis,
    logAxis: axis
  }
}
