import { defineNuxtPlugin } from '#app'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  TreemapChart,
  MapChart
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
  DataZoomComponent
} from 'echarts/components'

export default defineNuxtPlugin((nuxtApp) => {
  use([
    CanvasRenderer,
    BarChart,
    LineChart,
    PieChart,
    ScatterChart,
    TreemapChart,
    MapChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
    VisualMapComponent,
    DataZoomComponent
  ])

  nuxtApp.vueApp.component('VChart', VChart)
})
