import { registerMap } from 'echarts/core'

export const WORLD_MAP_NAME = 'world'

const ANTARCTICA = 'ATA'

interface WorldGeoJson {
  type: 'FeatureCollection'
  features: { properties: { iso3: string } }[]
}

let registration: Promise<void> | null = null

function registerWorld(): Promise<void> {
  registration ??= $fetch<WorldGeoJson>('/world-110m.json').then((geo) => {
    const features = geo.features.filter((feature) => feature.properties.iso3 !== ANTARCTICA)
    registerMap(WORLD_MAP_NAME, { ...geo, features } as unknown as Parameters<typeof registerMap>[1])
  })
  return registration
}

/** Charge les contours des pays une seule fois, à la première carte affichée. */
export function useWorldMap() {
  const isReady = ref(false)
  const hasError = ref(false)

  onMounted(async () => {
    try {
      await registerWorld()
      isReady.value = true
    } catch {
      registration = null
      hasError.value = true
    }
  })

  return { isReady, hasError }
}
