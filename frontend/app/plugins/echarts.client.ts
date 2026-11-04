/**
 * Enregistre les composants ECharts utilisés dans l'app.
 * .client.ts → ne tourne que dans le navigateur (pas de SSR).
 */
import VueECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { MapChart } from 'echarts/charts'
import {
  TooltipComponent,
  VisualMapComponent,
  TitleComponent,
} from 'echarts/components'

use([CanvasRenderer, MapChart, TooltipComponent, VisualMapComponent, TitleComponent])

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('VChart', VueECharts)
})
