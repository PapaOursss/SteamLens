<template>
  <div class="map-container">
    <div class="map-controls">
      <span class="hint-text">Cliquez ou survolez une zone du globe pour explorer ses chiffres :</span>
      <div class="badge-group">
        <button
          v-for="reg in regionsList"
          :key="reg.id"
          class="region-btn"
          :class="{ active: selectedRegion === reg.id }"
          @click="selectRegion(reg.id)"
        >
          <span class="color-dot" :style="{ backgroundColor: reg.color }"></span>
          {{ reg.label }}
        </button>
      </div>
    </div>

    <!-- Carte SVG interactive du monde -->
    <div class="svg-wrapper">
      <svg
        viewBox="0 0 1000 500"
        class="world-svg"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <radialGradient id="oceanGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#0f172a" />
            <stop offset="100%" stop-color="#020617" />
          </radialGradient>
        </defs>

        <!-- Fond océan -->
        <rect width="1000" height="500" fill="url(#oceanGrad)" rx="12" />

        <!-- Lignes de latitude / longitude décoratives -->
        <g stroke="#1e293b" stroke-width="0.5" stroke-dasharray="3,3" opacity="0.6">
          <line x1="50" y1="250" x2="950" y2="250" />
          <line x1="50" y1="125" x2="950" y2="125" />
          <line x1="50" y1="375" x2="950" y2="375" />
          <line x1="500" y1="50" x2="500" y2="450" />
        </g>

        <!-- Zone : Amérique du Nord (NA) -->
        <g
          class="region-group"
          :class="{ selected: selectedRegion === 'na', hovered: hoveredRegion === 'na' }"
          @click="selectRegion('na')"
          @mouseenter="hoveredRegion = 'na'"
          @mouseleave="hoveredRegion = null"
        >
          <path class="land land-na" d="M 120 70 L 220 50 L 310 60 L 340 100 L 290 140 L 210 130 L 170 150 L 110 120 Z" />
          <path class="land land-na" d="M 150 150 L 290 140 L 320 180 L 290 230 L 200 230 L 160 200 Z" />
          <path class="land land-na" d="M 180 230 L 250 230 L 230 290 L 190 270 Z" />
          <text x="210" y="175" class="region-svg-label">NA</text>
        </g>

        <!-- Zone : Europe (EU) -->
        <g
          class="region-group"
          :class="{ selected: selectedRegion === 'eu', hovered: hoveredRegion === 'eu' }"
          @click="selectRegion('eu')"
          @mouseenter="hoveredRegion = 'eu'"
          @mouseleave="hoveredRegion = null"
        >
          <path class="land land-eu" d="M 520 60 L 550 50 L 570 90 L 540 130 L 520 100 Z" />
          <path class="land land-eu" d="M 460 110 L 485 105 L 480 140 L 460 130 Z" />
          <path class="land land-eu" d="M 470 140 L 550 125 L 610 130 L 600 190 L 550 210 L 480 210 L 465 170 Z" />
          <text x="530" y="165" class="region-svg-label">EU</text>
        </g>

        <!-- Zone : Japon (JP) -->
        <g
          class="region-group"
          :class="{ selected: selectedRegion === 'jp', hovered: hoveredRegion === 'jp' }"
          @click="selectRegion('jp')"
          @mouseenter="hoveredRegion = 'jp'"
          @mouseleave="hoveredRegion = null"
        >
          <path class="land land-jp" d="M 850 160 L 870 170 L 885 200 L 860 220 L 840 210 L 845 180 Z" />
          <circle cx="862" cy="190" r="32" class="jp-pulse-ring" />
          <text x="862" y="150" class="region-svg-label jp-text">🇯🇵 JP</text>
        </g>

        <!-- Zone : Reste du monde (Other) -->
        <g
          class="region-group"
          :class="{ selected: selectedRegion === 'other', hovered: hoveredRegion === 'other' }"
          @click="selectRegion('other')"
          @mouseenter="hoveredRegion = 'other'"
          @mouseleave="hoveredRegion = null"
        >
          <path class="land land-other" d="M 270 290 L 340 310 L 370 370 L 330 460 L 290 420 L 260 340 Z" />
          <path class="land land-other" d="M 470 220 L 570 220 L 600 290 L 570 390 L 520 410 L 480 320 Z" />
          <path class="land land-other" d="M 610 120 L 820 110 L 840 200 L 760 290 L 670 270 L 610 200 Z" />
          <path class="land land-other" d="M 780 340 L 880 330 L 890 410 L 800 420 Z" />
          <text x="315" y="380" class="region-svg-label sub">Amérique du Sud</text>
          <text x="530" y="320" class="region-svg-label sub">Afrique</text>
          <text x="710" y="190" class="region-svg-label sub">Asie</text>
          <text x="835" y="375" class="region-svg-label sub">Océanie</text>
        </g>
      </svg>
    </div>

    <!-- Fiche d'information détaillée -->
    <RegionalSalesDetail :active-info="activeInfo" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  type RegionKey,
  REGIONS_LIST,
  REGIONS_DATA
} from '~/types/regionalSales'
import RegionalSalesDetail from '~/components/RegionalSalesDetail.vue'

const selectedRegion = ref<RegionKey>('jp')
const hoveredRegion = ref<RegionKey | null>(null)
const regionsList = REGIONS_LIST

const activeInfo = computed(() => {
  const currentKey = hoveredRegion.value || selectedRegion.value
  return REGIONS_DATA[currentKey]
})

function selectRegion(key: RegionKey) {
  selectedRegion.value = key
}
</script>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.map-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.hint-text {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.badge-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.region-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.region-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.region-btn.active {
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.svg-wrapper {
  background: #020617;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid #1e293b;
}

.world-svg {
  width: 100%;
  height: auto;
  display: block;
}

.region-group {
  cursor: pointer;
}

.land {
  fill-opacity: 0.45;
  stroke-width: 1.5;
  stroke-linejoin: round;
  transition: all 0.25s ease;
}

.land-na { fill: #38bdf8; stroke: #0284c7; }
.land-eu { fill: #34d399; stroke: #059669; }
.land-jp { fill: #f43f5e; stroke: #e11d48; }
.land-other { fill: #fbbf24; stroke: #d97706; }

.region-group:hover .land,
.region-group.hovered .land {
  fill-opacity: 0.8;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.3));
}

.region-group.selected .land {
  fill-opacity: 0.95;
  stroke: #ffffff;
  stroke-width: 2;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.region-svg-label {
  fill: #f8fafc;
  font-size: 15px;
  font-weight: 800;
  text-anchor: middle;
  pointer-events: none;
  letter-spacing: 1px;
}

.region-svg-label.sub {
  font-size: 10px;
  fill: #94a3b8;
  font-weight: 600;
}

.jp-text {
  font-size: 13px;
  fill: #fecdd3;
}

.jp-pulse-ring {
  fill: none;
  stroke: #f43f5e;
  stroke-width: 1.5;
  stroke-dasharray: 4, 3;
  animation: pulse 2.5s infinite linear;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.9; transform-origin: 862px 190px; }
  50% { transform: scale(1.15); opacity: 0.4; transform-origin: 862px 190px; }
  100% { transform: scale(0.95); opacity: 0.9; transform-origin: 862px 190px; }
}
</style>
