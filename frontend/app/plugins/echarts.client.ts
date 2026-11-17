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
  SankeyChart
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
  DataZoomComponent,
  CalendarComponent
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
    GridComponent,
    TooltipComponent,
    LegendComponent,
    VisualMapComponent,
    DataZoomComponent,
    CalendarComponent
  ])

  registerLocale('FR', frenchLocale)
  nuxtApp.vueApp.component('VChart', VChart)
})
