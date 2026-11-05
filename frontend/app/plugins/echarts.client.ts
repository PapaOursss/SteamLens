import { defineNuxtPlugin } from '#app'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart,
  LineChart,
  TreemapChart,
  SunburstChart,
  MapChart
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
  DataZoomComponent
} from 'echarts/components'

export default defineNuxtPlugin((nuxtApp) => {
  use([
    CanvasRenderer,
    BarChart,
    LineChart,
    TreemapChart,
    SunburstChart,
    MapChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    VisualMapComponent,
    DataZoomComponent
  ])

  nuxtApp.vueApp.component('VChart', VChart)
})
