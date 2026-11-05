import type { GameOption } from '~/composables/useGameSearch'

/** Jeu affiché sans choix : payant, suivi, et dont les prix sont relevés. */
const DEFAULT_APPID = 1091500

/** Le jeu d'une page vit dans l'adresse (`?appid=`), pour qu'elle reste partageable. */
export function useGameFromRoute() {
  const route = useRoute()
  const appid = computed(() => Number(route.query.appid) || DEFAULT_APPID)

  function selectGame(game: GameOption) {
    navigateTo({ query: { ...route.query, appid: game.appid } })
  }

  return { appid, selectGame }
}
