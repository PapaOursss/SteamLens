/** Thème ECharts commun : ce qu'un graphique ne règle pas lui-même vient d'ici. */
export function chartTheme() {
  const axis = { ...axisStyle(), nameTextStyle: { color: COLORS.soft } }
  return {
    color: [...SERIES_COLORS, '#3FB58A', '#9B7BE0', '#D96B3C', '#7FA83A', '#5C7CFA'],
    backgroundColor: 'transparent',
    ...chartBase(),
    legend: { textStyle: { color: COLORS.text }, inactiveColor: COLORS.line },
    categoryAxis: axis,
    valueAxis: axis,
    timeAxis: axis,
    logAxis: axis
  }
}
