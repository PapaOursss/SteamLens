<template>
  <div class="sunburst-wrapper">
    <div class="chart-container">
      <svg viewBox="-260 -260 520 520" class="sunburst-svg">
        <g v-for="slice in slices" :key="slice.id">
          <path
            :d="slice.path"
            :fill="slice.color"
            class="slice-path"
            :class="{ active: hoveredSlice?.id === slice.id }"
            @mouseenter="hoveredSlice = slice"
            @mouseleave="hoveredSlice = null"
          />
          <text
            v-if="slice.showLabel"
            :transform="slice.labelTransform"
            text-anchor="middle"
            dominant-baseline="central"
            class="slice-label"
          >
            {{ slice.shortName }}
          </text>
        </g>
        <circle r="48" fill="#1e293b" />
        <text text-anchor="middle" dominant-baseline="central" class="center-title">
          IGDB
        </text>
      </svg>
    </div>

    <div class="details-card">
      <div v-if="hoveredSlice">
        <span class="badge" :style="{ backgroundColor: hoveredSlice.color }">
          {{ hoveredSlice.levelName }}
        </span>
        <h4 class="details-name">{{ hoveredSlice.name }}</h4>
        <div class="details-metric">
          <strong class="metric-val">{{ hoveredSlice.value }}</strong> jeux
        </div>
        <p class="details-path">{{ hoveredSlice.breadcrumb }}</p>
      </div>
      <div v-else class="details-empty">
        <p>Survolez un segment du disque pour afficher ses détails.</p>
        <span class="hint">Centre : Genres → Milieu : Thèmes → Bord : Modes</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

export interface SunburstMode { name: string; value: number }
export interface SunburstTheme { name: string; value: number; children?: SunburstMode[] }
export interface SunburstGenre { name: string; value: number; children?: SunburstTheme[] }

interface ArcSlice {
  id: string
  name: string
  shortName: string
  value: number
  levelName: string
  breadcrumb: string
  path: string
  color: string
  showLabel: boolean
  labelTransform: string
}

const props = defineProps<{ data: SunburstGenre[] }>()
const hoveredSlice = ref<ArcSlice | null>(null)

const GENRE_COLORS: Record<string, string[]> = {
  'Role-playing (RPG)': ['#6366f1', '#818cf8', '#a5b4fc'],
  'Shooter': ['#ef4444', '#f87171', '#fca5a5'],
  'Simulator': ['#10b981', '#34d399', '#6ee7b7'],
  'Action': ['#f59e0b', '#fbbf24', '#fde68a'],
  'Default': ['#8b5cf6', '#a78bfa', '#c4b5fd']
}

function polarToCartesian(r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180.0
  return { x: r * Math.cos(rad), y: r * Math.sin(rad) }
}

function makeArc(rIn: number, rOut: number, a0: number, a1: number): string {
  const p0 = polarToCartesian(rIn, a0), p1 = polarToCartesian(rOut, a0)
  const p2 = polarToCartesian(rOut, a1), p3 = polarToCartesian(rIn, a1)
  const large = a1 - a0 > 180 ? 1 : 0
  return `M ${p0.x} ${p0.y} L ${p1.x} ${p1.y} A ${rOut} ${rOut} 0 ${large} 1 ${p2.x} ${p2.y} L ${p3.x} ${p3.y} A ${rIn} ${rIn} 0 ${large} 0 ${p0.x} ${p0.y} Z`
}

const slices = computed<ArcSlice[]>(() => {
  const result: ArcSlice[] = []
  const total = props.data.reduce((acc, g) => acc + g.value, 0) || 1
  let currentAngle = 0

  props.data.forEach((genre, gIdx) => {
    const genreSpan = (genre.value / total) * 360
    const gStart = currentAngle, gEnd = currentAngle + genreSpan
    const palette = GENRE_COLORS[genre.name] || GENRE_COLORS.Default

    pushSlice(result, {
      id: `g-${gIdx}`, name: genre.name, value: genre.value,
      levelName: 'Genre', breadcrumb: genre.name,
      rIn: 52, rOut: 115, a0: gStart, a1: gEnd, color: palette[0]
    })

    let tAngle = gStart
    const gTotal = genre.children?.reduce((acc, t) => acc + t.value, 0) || genre.value
    genre.children?.forEach((theme, tIdx) => {
      const themeSpan = (theme.value / gTotal) * genreSpan
      const tStart = tAngle, tEnd = tAngle + themeSpan
      pushSlice(result, {
        id: `g-${gIdx}-t-${tIdx}`, name: theme.name, value: theme.value,
        levelName: 'Thème', breadcrumb: `${genre.name} > ${theme.name}`,
        rIn: 120, rOut: 180, a0: tStart, a1: tEnd, color: palette[1]
      })

      let mAngle = tStart
      const tTotal = theme.children?.reduce((acc, m) => acc + m.value, 0) || theme.value
      theme.children?.forEach((mode, mIdx) => {
        const modeSpan = (mode.value / tTotal) * themeSpan
        pushSlice(result, {
          id: `g-${gIdx}-t-${tIdx}-m-${mIdx}`, name: mode.name, value: mode.value,
          levelName: 'Mode de jeu', breadcrumb: `${genre.name} > ${theme.name} > ${mode.name}`,
          rIn: 185, rOut: 245, a0: mAngle, a1: mAngle + modeSpan, color: palette[2]
        })
        mAngle += modeSpan
      })
      tAngle += themeSpan
    })
    currentAngle = gEnd
  })
  return result
})

function pushSlice(list: ArcSlice[], item: {
  id: string; name: string; value: number; levelName: string;
  breadcrumb: string; rIn: number; rOut: number; a0: number; a1: number; color: string
}) {
  const span = item.a1 - item.a0
  if (span <= 0.5) return
  const path = makeArc(item.rIn, item.rOut, item.a0, item.a1 - 0.4)
  const pos = polarToCartesian((item.rIn + item.rOut) / 2, item.a0 + span / 2)
  list.push({
    id: item.id, name: item.name,
    shortName: item.name.length > 10 ? `${item.name.slice(0, 8)}…` : item.name,
    value: item.value, levelName: item.levelName, breadcrumb: item.breadcrumb,
    path, color: item.color, showLabel: span > 14,
    labelTransform: `translate(${pos.x}, ${pos.y})`
  })
}
</script>

<style scoped>
.sunburst-wrapper {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
  gap: 2rem; background: #ffffff; padding: 1.5rem;
  border: 1px solid #e2e8f0; border-radius: 0.75rem;
}
.chart-container { width: 100%; max-width: 480px; aspect-ratio: 1; }
.sunburst-svg { width: 100%; height: 100%; }
.slice-path {
  cursor: pointer; stroke: #ffffff; stroke-width: 1.5;
  transition: opacity 0.2s, filter 0.2s;
}
.slice-path:hover, .slice-path.active { opacity: 0.9; filter: brightness(1.15); }
.slice-label {
  fill: #ffffff; font-size: 8px; font-weight: 700;
  pointer-events: none; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.7);
}
.center-title { fill: #ffffff; font-size: 14px; font-weight: 800; }
.details-card {
  flex: 1; min-width: 250px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1.25rem;
}
.details-empty { color: #64748b; font-size: 0.9rem; line-height: 1.5; }
.details-empty .hint { display: block; margin-top: 0.75rem; font-size: 0.8rem; color: #94a3b8; }
.badge {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px;
  color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem;
}
.details-name { font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem 0; }
.details-metric { font-size: 1.1rem; color: #334155; margin-bottom: 0.5rem; }
.metric-val { font-size: 1.4rem; color: #0f172a; }
.details-path { font-size: 0.85rem; color: #64748b; margin: 0; font-family: monospace; }
</style>
