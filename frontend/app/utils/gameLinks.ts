const STEAM_CDN = 'https://cdn.akamai.steamstatic.com/steam/apps'

/** Là où mène un clic sur un jeu. La fiche jeu (T-14) n'existe pas encore : à changer ici seul. */
export function gameLink(appid: number): string {
  return `/pricing?appid=${appid}`
}

/** Image large : celle de l'API, sinon celle du CDN Steam déduite de l'appid. */
export function wideCoverSources(appid: number, headerImage = ''): string[] {
  const fromCdn = `${STEAM_CDN}/${appid}/header.jpg`
  return headerImage ? [headerImage, fromCdn] : [fromCdn]
}

/** Jaquette verticale pour les tuiles hautes (la large y serait floue), sinon la large. */
export function tallCoverSources(appid: number, headerImage = ''): string[] {
  return [`${STEAM_CDN}/${appid}/library_600x900_2x.jpg`, ...wideCoverSources(appid, headerImage)]
}

/** Grande image de bandeau (1920 px) pour les très grandes tuiles, sinon la large. */
export function heroCoverSources(appid: number, headerImage = ''): string[] {
  return [`${STEAM_CDN}/${appid}/library_hero.jpg`, ...wideCoverSources(appid, headerImage)]
}
