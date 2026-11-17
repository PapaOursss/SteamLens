import { defineNuxtPlugin } from '#app'
import VChart from 'vue-echarts'
import { registerLocale, use } from 'echarts/core'
import frenchLocale from 'echarts/i18n/langFR-obj'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart,
  LineChart,
  TreemapChart,
  SunburstChart,
  MapChart,
  HeatmapChart,
  GraphChart,
  ScatterChart,
  ThemeRiverChart,
  SankeyChart,
  RadarChart
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
  DataZoomComponent,
  CalendarComponent,
  RadarComponent
} from 'echarts/components'

export default defineNuxtPlugin((nuxtApp) => {
  use([
    CanvasRenderer,
    BarChart,
    LineChart,
    TreemapChart,
    SunburstChart,
    MapChart,
    HeatmapChart,
    GraphChart,
    ScatterChart,
    ThemeRiverChart,
    SankeyChart,
    RadarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    VisualMapComponent,
    DataZoomComponent,
    CalendarComponent,
    RadarComponent
  ])

  registerLocale('FR', frenchLocale)
  nuxtApp.vueApp.component('VChart', VChart)
})
