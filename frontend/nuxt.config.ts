// https://nuxt.com/docs/api/configuration/nuxt-config
import { PALETTES, THEME_BOOT_SCRIPT, THEME_STYLESHEET } from './app/utils/palettes'

const COLORS = Object.fromEntries(
  Object.keys(PALETTES.dark).map((name) => [name, `rgb(var(--${name}) / <alpha-value>)`])
)

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  tailwindcss: {
    config: {
      theme: {
        extend: {
          colors: COLORS,
          fontFamily: {
            sans: ['"Instrument Sans"', 'system-ui', 'sans-serif'],
            display: ['"Bricolage Grotesque"', 'system-ui', 'sans-serif']
          },
          maxWidth: { prose: '68ch' }
        }
      }
    }
  },
  components: [{ path: '~/components', pathPrefix: false }],
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      htmlAttrs: { lang: 'fr' },
      meta: [{ name: 'theme-color', content: '#1B1F6B' }],
      style: [{ innerHTML: THEME_STYLESHEET }],
      script: [{ innerHTML: THEME_BOOT_SCRIPT }],
      link: [
        { rel: 'preload', as: 'font', type: 'font/woff2', href: '/fonts/bricolage-grotesque.woff2', crossorigin: '' },
        { rel: 'preload', as: 'font', type: 'font/woff2', href: '/fonts/instrument-sans.woff2', crossorigin: '' }
      ]
    }
  },
  experimental: { viewTransition: true },
  routeRules: {
    '/map': { redirect: '/pricing' }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api'
    }
  },
  build: {
    transpile: [/echarts/, 'vue-echarts']
  }
})

