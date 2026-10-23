# Backlog

Everything left to do on SteamLens, in a single list ordered by priority. Started on
**2026-10-21**. What is done is in the "✅ Done" section at the bottom; what was turned
down is in [rejected.md](rejected.md). **Nothing else is open.**

North star: **SteamLens montre, sur une carte et des graphiques interactifs, ce qui se joue sur
Steam, où, à quel prix et depuis quand — à partir d'au moins dix sources de données gratuites.**

---

## How to use (humans and agents)

**A ticket** = a `### T-NN · Title` heading, then five fixed lines, then the details:

    ### T-NN · Short title that says what to achieve
    - **Type**: task
    - **Status**: todo
    - **Opened**: YYYY-MM-DD
    - **Effort**: S · **Owner**: … · **Due**: —
    - **Origin**: where it comes from · audit `docs/_archive/<folder>/README.md` l. 10-20

    Why, what to do (as a `- [ ]` checklist when there are several steps), where to look.

- **ID** `T-NN`: stable, never reused, quoted as is in commits and branches.
  **Next free: T-51.**
- **Type**, one of: `bug` (something is broken); `improvement` (it works, it could work
  better); `idea` (nothing exists yet, to be explored); `task` (work that is neither: a release,
  a decision, a check).
- **Status**, one of: `todo`; `in progress — branch <name>, since YYYY-MM-DD`;
  `blocked — waiting for <who or what>`; `to verify — <where>`.
- **Priority** = the section the ticket lives in; changing it means moving the ticket.
  🔴 critical (now), 🟠 important (before the north star), 🟡 normal, ⚪ background
  (long-running work, debt, ideas still to be explored).
- **Effort**: XS (under an hour), S (half a day), M (one or two days), L (more).
- **Owner**: `—` (free, anyone may take it), a member's GitHub login (`@login`) or first name
  (the ticket is reserved for them), `Claude` (an agent's job), or `contributor — #NN` (kept for
  an outside contributor). An agent only works on a free ticket or one owned by the account it
  works for (`gh api user --jq .login`): it skips the others and, asked for one, says who owns
  it instead of doing it. **Each member writes only their own login**: taking a free ticket, or
  turning their own first name into their login; never someone else's (only the owner hands a
  ticket over).
- **Releases**: the `## 🚀 Releases` section at the top places every open ticket in a planned
  release (`/kiln:backlog plan`); numbers are planned, not promised, until the candidate is cut.
- **Closing a ticket**: remove it from its section and add a line at the top of the "✅ Done"
  log: `- **YYYY-MM-DD** · T-NN · Title — what was done (branch) · opened YYYY-MM-DD`.
- **Details in archived audits**: when a ticket quotes lines of `docs/_archive/`, the original
  finding is there in full; it is old, check it against the current code.
- **Locations quoted are hints, not addresses.**
- Overview: `grep -E '^(## |### T-|- \*\*Status)' docs/backlog/backlog.md`.

---

## 🚀 Releases

- **v1 « Ça s'affiche »** — fondations, trois sources, premières vues : T-01 à T-17.
- **v2 « Le monde entier »** — plus de sources, les cartes du monde et les graphiques
  originaux : T-18 à T-36, T-49, T-50.
- **v3 « Bonus pour la soutenance »** — idées fun et données en plus : T-37 à T-48.

## 🧭 Vue d'ensemble

**Sources gratuites visées** (clé = inscription gratuite, voir [urgent.md](urgent.md)) :

| Source | Clé | Ce qu'on en tire | Ticket |
|---|---|---|---|
| Kaggle — Steam Games Complete (trolukovich) | compte Kaggle | catalogue, genres, tags, prix, dates | T-06 |
| Kaggle — Steam Games Dataset (fronkongames) | compte Kaggle | catalogue récent, CCU, temps de jeu | T-07 |
| Kaggle — Steam Reviews, vgsales, historiques de joueurs | compte Kaggle | avis, ventes par région, joueurs par mois | T-28, T-44, T-47 |
| SteamSpy API | non | propriétaires estimés, tags pondérés, top 100 | T-08 |
| Steam Web API (officielle) | oui | joueurs en direct, succès, actus, pays des profils | T-09, T-35, T-37 |
| Steam Store API (non documentée) | non | fiche, prix par pays, avis par langue | T-10, T-22 |
| Steam Hardware & Software Survey | non (page) | langues, OS, GPU des joueurs | T-27 |
| IGDB | oui (Twitch) | genres, thèmes, modes, PopScore | T-11 |
| RAWG | oui | notes, Metacritic, tags | T-20 |
| Twitch Helix | oui (même appli qu'IGDB) | jeux les plus streamés | T-21 |
| IsThereAnyDeal | oui | historique des prix | T-18 |
| CheapShark | non | promos, plus bas prix tous magasins | T-19 |
| Google Trends (pytrends) | non | intérêt par pays | T-24 |
| Wikidata SPARQL | non | pays des studios | T-26 |
| Banque mondiale | non | PIB par habitant (pouvoir d'achat) | T-25 |
| Frankfurter (taux BCE) | non | conversion des prix en euros | T-16 |
| REST Countries + Natural Earth | non | noms, codes ISO, contours des pays | T-16 |
| ProtonDB | non | compatibilité Linux / Steam Deck | T-38 |
| GamerPower | non | jeux offerts en ce moment | T-48 |

**Choix techniques proposés** : Django + Django REST Framework, une app par domaine
(`catalog`, `pricing`, `players`, `geography`, `ingestion`) ; une commande `manage.py` par
source pour importer ; SQLite pour commencer (PostgreSQL dans `compose.yml` si ça rame) ;
polars pour les gros CSV Kaggle ; Nuxt 4 + Tailwind + **ECharts** (`vue-echarts`), qui fait
d'un coup cartes, treemap, sunburst, sankey, graphe, streamgraph, calendrier et bar race.

**Règle d'or des données** : le front ne parle qu'à notre backend, jamais aux API ; le
backend importe, met en cache et sert des agrégats. Aucune donnée personnelle stockée
(pas de SteamID, pas de pseudo) : seulement des comptes par pays, langue ou jeu.

---

## 🔴 Critical

### T-01 · Backend Django prêt à servir une API REST
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: plan initial du projet

Socle sur lequel tout le reste se branche.
- [ ] `uv add djangorestframework django-cors-headers django-filter`
- [ ] Créer les apps `catalog`, `pricing`, `players`, `geography`, `ingestion`
- [ ] CORS ouvert sur `http://localhost:3000` en dev
- [ ] Route `/api/health/` qui répond `{"status": "ok"}`
- [ ] Régénérer `requirements.txt` (`uv export …`, voir `GEMINI.md`)

### T-02 · Modèle de données commun à toutes les sources
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: plan initial du projet

La clé de voûte : **l'appid Steam** relie toutes les sources. Une classe par fichier.
- [ ] `Game` (appid, nom, date de sortie, gratuit ?, image, ids externes IGDB / RAWG / ITAD)
- [ ] `Genre`, `Tag` (avec poids des votes), `Theme`, `GameMode`, `Platform`
- [ ] `Company` (développeur / éditeur, pays d'origine)
- [ ] `Country` (ISO-2, ISO-3, nom français, continent, langue principale)
- [ ] `PricePoint` (jeu, pays, devise, prix, prix en euros, remise, date, source)
- [ ] `PlayerCountSnapshot` (jeu, date-heure, joueurs connectés, source)
- [ ] `ReviewSummary` (jeu, langue, positifs, négatifs, date)
- [ ] `ImportRun` (source, début, fin, nombre de lignes, erreurs) pour suivre les imports
- [ ] Schéma dessiné dans `docs/donnees.md`

### T-03 · Clés d'API en variables d'environnement
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Antoine · **Due**: —
- **Origin**: règle « jamais de secret dans le code » (`GEMINI.md`)

- [ ] `uv add django-environ`, lecture de `backend/.env` (ignoré par git)
- [ ] `backend/.env.example` commité avec toutes les variables vides : `STEAM_API_KEY`,
  `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `RAWG_API_KEY`, `ITAD_API_KEY`,
  `KAGGLE_USERNAME`, `KAGGLE_KEY`
- [ ] Une source dont la clé manque est sautée avec un message clair, sans planter
- [ ] `compose.yml` : `env_file: backend/.env`

### T-04 · Client HTTP partagé : cache, débit limité, reprises
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: limites des API gratuites

Toutes les API gratuites limitent le débit ; se faire bannir pendant la démo serait bête.
- [ ] `uv add httpx requests-cache tenacity` (ou `hishel` pour le cache httpx)
- [ ] Une classe `ApiClient` dans `ingestion/` : cache disque, pause entre deux appels,
  reprise exponentielle sur 429 / 5xx
- [ ] Limites à régler par source : Steam Store ~200 req / 5 min, SteamSpy 1 req/s
  (`request=all` : 1 req/min), IGDB 4 req/s, Twitch 800 points/min, RAWG 20 000 req/mois
- [ ] Les réponses brutes de test sont enregistrées en fixtures (voir T-49)

### T-05 · Front Nuxt : Tailwind, ECharts, mise en page et navigation
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: plan initial du projet

- [ ] Installer `@nuxtjs/tailwindcss`, `echarts`, `vue-echarts`
- [ ] Layout : barre latérale (Accueil, Jeux, Genres, Monde, Prix, Tendances, Labo)
- [ ] Composable `useApi()` qui appelle le backend (`runtimeConfig.public.apiBase`)
- [ ] Composant `ChartCard.vue` réutilisable : titre, source citée, état « chargement »
  et « pas de données »
- [ ] Types TypeScript des réponses dans `types/`

### T-06 · Import Kaggle « Steam Games Complete Dataset »
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Nathan · **Due**: —
- **Origin**: `docs/suivi.md` · kaggle.com/datasets/trolukovich/steam-games-complete-dataset

Première vraie donnée : ~40 000 jeux avec genres, tags, prix, dates, avis.
- [ ] Téléchargement par `uv add kaggle` (ou à la main dans `backend/data/raw/`, ignoré)
- [ ] `manage.py import_kaggle_steam_complete` : nettoyage avec polars, appid tiré de l'URL,
  dates en ISO, prix en euros, tags éclatés
- [ ] Import idempotent (relancer ne crée pas de doublons) ; trace dans `ImportRun`

## 🟠 Important

### T-07 · Import Kaggle « Steam Games Dataset » (fronkongames)
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Nathan · **Due**: —
- **Origin**: kaggle.com/datasets/fronkongames/steam-games-dataset

Plus récent et plus gros (~100 000 jeux) : pic de joueurs, temps de jeu moyen, langues
supportées, Metacritic, propriétaires estimés.
- [ ] Fusion par appid avec T-06 : la donnée la plus récente gagne
- [ ] Garder les « langues supportées » : elles servent aux cartes (T-23)

### T-08 · SteamSpy : propriétaires, joueurs, tags pondérés
- **Type**: task
- **Status**: in progress — branch feat/T-08-steamspy, since 2026-10-23
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: @NathanBarrachin · **Due**: —
- **Origin**: steamspy.com/api.php (sans clé)

Client et lecture des réponses faits dans `backend/ingestion/sources/steamspy/` (testés sur
fixtures) ; il reste à enregistrer en base, ce qui attend les modèles de T-02.
- [x] `request=all&page=N` (1 000 jeux par page, 1 appel/min) pour la base
- [x] `request=appdetails&appid=` pour les tags avec leur nombre de votes
- [x] `request=top100in2weeks` et `top100forever` pour les classements
- [x] Les fourchettes « 1 000 000 .. 2 000 000 » lues en min / max / milieu
- [ ] `manage.py import_steamspy` vers `Game`, `Tag` et `ImportRun` (après T-02)

### T-09 · Steam Web API : joueurs connectés en direct et historique maison
- **Type**: task
- **Status**: in progress — branch feat/T-09-player-count, since 2026-10-23
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: @NathanBarrachin · **Due**: —
- **Origin**: steamcommunity.com/dev · `ISteamUserStats/GetNumberOfCurrentPlayers`

Pas d'historique officiel : on le fabrique nous-mêmes en photographiant les joueurs.
`GetNumberOfCurrentPlayers` marche **sans clé** : client fait dans
`backend/ingestion/sources/steam_web_api/` (branche partie de T-08). La commande attend
`PlayerCountSnapshot` (T-02).
- [x] Client `PlayerCountClient.snapshot(appids)` (un appel toutes les 0,5 s, 404 = jeu ignoré)
- [ ] `manage.py snapshot_players` sur le top 500 (SteamSpy) → `PlayerCountSnapshot`
- [ ] Le lancer toutes les heures (cron du poste ou T-45) dès que possible : plus on commence
  tôt, plus les courbes seront belles à la soutenance
- [ ] Compléter le passé avec un dataset Kaggle d'historique SteamCharts (voir T-28)

### T-10 · Steam Store : fiche détaillée et prix dans chaque pays
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Nathan · **Due**: —
- **Origin**: `store.steampowered.com/api/appdetails?appids=&cc=` (sans clé, non documentée)

- [ ] Fiche : description courte, captures, catégories, configuration, développeurs
- [ ] Prix : même jeu interrogé avec `cc=fr,us,gb,br,ar,tr,ru,in,cn,jp,…` (~40 pays),
  `filters=price_overview` pour alléger
- [ ] Respecter ~200 req / 5 min : file d'attente, top 1 000 jeux seulement

### T-11 · IGDB : genres, thèmes, modes de jeu et PopScore
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Nathan · **Due**: —
- **Origin**: api-docs.igdb.com (jeton Twitch « client credentials »)

IGDB a une classification plus fine que Steam.
- [ ] Jeton OAuth Twitch renouvelé automatiquement
- [ ] Lien appid ↔ IGDB par l'endpoint `external_games` (source Steam)
- [ ] Genres, thèmes (horreur, SF…), `game_modes`, `player_perspectives`, studios et pays
- [ ] `popularity_primitives` (PopScore : visites, envies, joueurs) pour un second avis
  sur la popularité

### T-12 · API du backend : un endpoint par visualisation
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: règle d'or des données (Vue d'ensemble)

Le backend renvoie des données déjà agrégées, prêtes à tracer.
- [ ] `/api/games/?search=&genre=&tag=&order=` paginé
- [ ] `/api/games/<appid>/` et `/api/games/<appid>/players/`, `/prices/`
- [ ] `/api/stats/genres/`, `/api/stats/tags/`, `/api/stats/top-played/`
- [ ] `/api/map/<indicateur>/` qui renvoie `{iso3: valeur}` pour toutes les cartes
- [ ] Documentation automatique (`drf-spectacular`, page `/api/docs/`)

### T-13 · Page d'accueil : tableau de bord en direct
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Léandre · **Due**: —
- **Origin**: plan initial du projet

- [ ] Tuiles chiffres clés : jeux suivis, joueurs connectés au total, genre roi, prix moyen
- [ ] Top 10 des jeux les plus joués maintenant (barres horizontales + jaquette)
- [ ] Mini-courbe (sparkline) des 24 dernières heures sur chaque ligne
- [ ] Bandeau « jeu du jour » tiré au hasard parmi les pépites (T-30)

### T-14 · Fiche jeu complète
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: L · **Owner**: Léandre · **Due**: —
- **Origin**: plan initial du projet

- [ ] En-tête : jaquette, genres, studio, date, prix en France, note
- [ ] Courbe des joueurs connectés (zoom jour / mois / année)
- [ ] Courbe du prix avec les promos marquées (après T-18)
- [ ] Radar « ADN du jeu » : note, popularité, prix, durée de vie, buzz Twitch, rareté des
  succès (chaque axe normalisé de 0 à 100)
- [ ] Mini-carte du prix dans le monde (T-16)

### T-15 · Treemap et sunburst des genres et tags
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] Treemap genre → tags, surface = propriétaires estimés, couleur = note moyenne
- [ ] Bascule « nombre de jeux » / « nombre de joueurs » : on voit que les jeux indés sont
  partout mais qu'une poignée de genres prend les joueurs
- [ ] Sunburst équivalent avec les genres IGDB (genre → thème → mode)

### T-16 · Carte du monde n°1 : le prix d'un jeu dans chaque pays
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: plan initial du projet

Première carte, la plus simple : les données viennent de T-10.
- [ ] Contours des pays : GeoJSON Natural Earth 110m dans `frontend/public/`
- [ ] Conversion en euros avec Frankfurter (`api.frankfurter.app/latest?from=EUR`, taux BCE)
- [ ] Noms et codes des pays avec REST Countries (`restcountries.com/v3.1/all`)
- [ ] Carte choroplèthe ECharts + classement « où l'acheter le moins cher »
- [ ] Sélecteur de jeu en haut de la carte

### T-17 · Recherche de jeu avec autocomplétion
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Léandre · **Due**: —
- **Origin**: plan initial du projet

- [ ] Barre de recherche globale (raccourci `/`), suggestions avec jaquette dès 2 lettres
- [ ] Côté backend : `icontains` d'abord, recherche floue plus tard si besoin

## 🟡 Normal

### T-18 · IsThereAnyDeal : historique des prix
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: docs.isthereanydeal.com (clé gratuite)

La « vraie » évolution des prix demandée dans `docs/suivi.md`.
- [ ] Lien appid → id ITAD (`games/lookup`)
- [ ] `games/history` : chaque changement de prix sur Steam depuis des années
- [ ] Plus bas historique, nombre de promos par an, remise moyenne
- [ ] Vue « calendrier des soldes Steam » : on voit les soldes d'été et d'hiver revenir

### T-19 · CheapShark : promos du moment, tous magasins
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Léandre · **Due**: —
- **Origin**: cheapshark.com/api (sans clé)

- [ ] `deals?steamAppID=` : prix sur Steam, GOG, Humble, Fanatical…
- [ ] Graphique « Steam est-il le moins cher ? » : barres par magasin pour un jeu
- [ ] Page « bonnes affaires » : les plus grosses remises du jour sur les jeux bien notés

### T-20 · RAWG : notes, Metacritic et tags complémentaires
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Léandre · **Due**: —
- **Origin**: rawg.io/apidocs (clé gratuite, 20 000 req/mois)

- [ ] Note des joueurs RAWG, Metacritic, temps de jeu, captures supplémentaires
- [ ] Croisement « note presse vs note Steam » (nuage de points, diagonale = accord)

### T-21 · Twitch : les jeux les plus regardés
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Léandre · **Due**: —
- **Origin**: dev.twitch.tv/docs/api (même application que pour IGDB)

- [ ] `helix/games/top` + somme des spectateurs de `helix/streams?game_id=` toutes les heures
- [ ] Langue des streams (`language`) gardée : elle nourrit les cartes (T-23)
- [ ] Passé complété par un dataset Kaggle des top jeux Twitch 2016-2023 (à vérifier)

### T-22 · Avis Steam : volume, ratio positif et langue
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: `store.steampowered.com/appreviews/<appid>?json=1` (sans clé)

- [ ] `query_summary` par langue (`language=french`, `english`, `schinese`…) → `ReviewSummary`
- [ ] Courbe du ratio positif dans le temps (`filter=recent`, pagination par `cursor`)
- [ ] Détecter les « review bombings » : chute brutale du ratio sur une semaine
- [ ] Ne stocker ni l'auteur ni son SteamID, seulement des comptes

### T-23 · Carte du monde n°2 : quels genres joue-t-on par pays ?
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: demande de l'équipe (carte des styles de jeu par pays)

Steam ne donne pas les joueurs par pays : on l'approche par **la langue des avis** (T-22) et
des streams Twitch (T-21), reportée sur les pays qui parlent cette langue.
- [ ] Table langue → pays (pondérée par la population, via REST Countries)
- [ ] Pour chaque pays : genre le plus surreprésenté par rapport à la moyenne mondiale
  (indice de spécificité, pas juste le plus joué, sinon c'est « Action » partout)
- [ ] Carte : couleur = genre dominant ; clic sur un pays = barres de ses 10 genres
- [ ] Encadré honnête « comment c'est calculé et pourquoi c'est approximatif »

### T-24 · Carte du monde n°3 : l'intérêt pour un jeu selon Google Trends
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Sterenn · **Due**: —
- **Origin**: Google Trends (`pytrends`, non officiel)

- [ ] `interest_by_region` pour le top 50 des jeux et les grands genres (« jeu de survie »…)
- [ ] Carte animée dans le temps (curseur par mois) : on voit un jeu « se propager »
- [ ] `pytrends` est fragile (bloqué souvent) : résultats mis en cache longtemps, plan B =
  export CSV à la main depuis trends.google.com

### T-25 · Carte du monde n°4 : le prix rapporté au pouvoir d'achat
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: api.worldbank.org (sans clé)

« Combien d'heures de travail coûte un jeu à 60 € selon le pays ? »
- [ ] Indicateurs Banque mondiale : PIB par habitant en parité de pouvoir d'achat
  (`NY.GDP.PCAP.PP.CD`), population (`SP.POP.TOTL`)
- [ ] Indice = prix local converti ÷ revenu ; carte + classement
- [ ] Montrer l'effet des prix régionaux de Steam (Turquie, Argentine…) avant / après

### T-26 · Carte du monde n°5 : d'où viennent les studios ?
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Dorian · **Due**: —
- **Origin**: query.wikidata.org (SPARQL, sans clé)

- [ ] Requête SPARQL : jeux avec un Steam application ID (P1733) → développeur (P178) →
  pays (P17 / P495) ; compléter avec les pays des studios IGDB (T-11)
- [ ] Carte des studios par pays + genre de prédilection de chaque pays
- [ ] Flux (lignes courbes) « pays du studio → pays où le jeu est joué » en bonus

### T-27 · Enquête matériel et logiciels de Steam
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: store.steampowered.com/hwsurvey (page publique, chiffres mensuels)

Seule source officielle sur **qui** sont les joueurs.
- [ ] Récupérer chaque mois : langues, OS, cartes graphiques, RAM, VR
- [ ] Courbes : montée du chinois simplifié, part de Linux et du Steam Deck, GPU dominants
- [ ] Les langues recalent les poids de la carte n°2 (T-23)

### T-28 · Bar chart race des jeux les plus joués
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Sterenn · **Due**: —
- **Origin**: dataset Kaggle d'historique SteamCharts (à choisir) + T-09

- [ ] Importer un historique mensuel de joueurs (pic et moyenne) depuis ~2012
- [ ] Course de barres animée ECharts (top 15 par mois), bouton lecture / pause
- [ ] Bump chart en alternative : rang de chaque jeu au fil des mois

### T-29 · Streamgraph : l'évolution des genres par année de sortie
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] Nombre de sorties par genre et par année (ThemeRiver ECharts)
- [ ] Annoter les moments clés : Steam Greenlight 2012, Steam Direct 2017, explosion des
  jeux indés, mode des roguelikes et des survival

### T-30 · Nuage de points « chercheur de pépites »
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] x = prix, y = % d'avis positifs, taille = propriétaires, couleur = genre
- [ ] Zone « pépites » surlignée : très bien noté, pas cher, peu connu
- [ ] Filtres par genre et par année ; clic = fiche jeu

### T-31 · Réseau des tags qui vont ensemble
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] Graphe de forces : nœud = tag (taille = nb de jeux), lien = co-occurrence (épaisseur)
- [ ] Communautés détectées (`networkx`, Louvain) colorées : on voit apparaître des
  « familles » (cozy / farming / pixel art, souls-like / difficile / sombre…)
- [ ] Limiter aux 150 tags principaux pour rester lisible

### T-32 · Sankey : genre → tranche de prix → accueil
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] Tranches : gratuit, < 5 €, 5-15 €, 15-30 €, > 30 € ; accueil : négatif, mitigé, positif,
  très positif
- [ ] Répond à « les jeux chers sont-ils mieux notés ? »

### T-33 · Calendrier des sorties
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Sterenn · **Due**: —
- **Origin**: plan initial du projet

- [ ] Heatmap jour de la semaine × mois du nombre de sorties (tout le monde sort le jeudi ?)
- [ ] Calendrier annuel façon contributions GitHub, une case par jour

### T-34 · Hype contre réalité : Twitch face à Steam
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: T-09 + T-21

- [ ] Double courbe spectateurs Twitch / joueurs Steam pour un jeu
- [ ] Ratio spectateurs ÷ joueurs : jeux « regardés plus que joués » vs « joués en silence »
- [ ] Classement des deux extrêmes

### T-35 · Succès : les jeux que personne ne finit
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: `ISteamUserStats/GetGlobalAchievementPercentagesForApp` (Steam Web API)

- [ ] Pourcentage de joueurs pour chaque succès du top 300
- [ ] « Courbe d'abandon » : succès triés par rareté, la pente montre où les joueurs lâchent
- [ ] Classement des jeux au plus faible taux de fin (succès de fin d'histoire)

### T-36 · Comparateur de jeux
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Léandre · **Due**: —
- **Origin**: plan initial du projet

- [ ] Choisir 2 à 4 jeux : radars superposés (T-14), courbes de joueurs et de prix alignées
- [ ] Lien partageable (`/comparer?ids=730,570`)

### T-49 · Tests sans réseau : fixtures des réponses d'API
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: fiabilité des imports

- [ ] Une réponse réelle par source enregistrée dans `backend/tests/fixtures/`
- [ ] Un test par commande d'import (parsing, idempotence) avec `respx` ou `responses`
- [ ] Un test par endpoint de T-12

### T-50 · Page « Sources et méthode » pour la soutenance
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: projet scolaire, à présenter

- [ ] Chaque source : logo, ce qu'on en tire, fraîcheur (dernier `ImportRun`), licence
- [ ] Limites honnêtes (propriétaires estimés, pays approximés par la langue…)
- [ ] Schéma du flux : sources → commandes d'import → base → API → graphiques

## ⚪ Background — long-running work, debt and ideas

### T-37 · Carte n°6 : pays déclarés des profils publics
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: L · **Owner**: Pavel · **Due**: —
- **Origin**: `ISteamUser/GetPlayerSummaries` (champ facultatif `loccountrycode`)

La carte la plus « vraie » des joueurs par pays, mais à manier avec soin.
- [ ] Échantillon : auteurs des avis récents d'un jeu (T-22) → `GetPlayerSummaries` par lots
  de 100 → on ne garde que le pays, compté par jeu et par genre
- [ ] **Aucun SteamID ni pseudo enregistré**, même temporairement sur disque
- [ ] Afficher la taille de l'échantillon et le % de profils sans pays

### T-38 · ProtonDB : jouable sous Linux et Steam Deck ?
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: `protondb.com/api/v1/reports/summaries/<appid>.json` (non officiel)

- [ ] Niveau (platinum, gold…) par jeu ; répartition par genre en barres empilées
- [ ] Badge sur la fiche jeu

### T-39 · Durée de vie des jeux par genre
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: temps de jeu moyen SteamSpy (T-08) et Kaggle (T-07)

- [ ] Ridgeline (courbes de densité empilées) du temps de jeu médian par genre
- [ ] « Prix par heure de jeu » : classement des jeux les plus rentables

### T-40 · Nuage de mots des avis positifs et négatifs
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: texte des avis (T-22, T-47)

- [ ] Mots les plus fréquents des avis 👍 et 👎 en deux nuages côte à côte (`echarts-wordcloud`)
- [ ] Mots vides retirés, une langue à la fois (anglais et français)

### T-41 · Jeux similaires par tags
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Pavel · **Due**: —
- **Origin**: tags pondérés SteamSpy (T-08)

- [ ] Vecteur de tags pondérés par jeu, similarité cosinus, 10 voisins précalculés
- [ ] Bloc « si tu aimes ce jeu… » sur la fiche ; projection 2D (UMAP / t-SNE) de tout le
  catalogue en nuage de points explorable

### T-42 · Mini-jeu « Plus ou moins »
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: idée fun pour la démo

- [ ] Deux jaquettes : lequel a le plus de joueurs / coûte le plus cher / est le mieux noté ?
- [ ] Score et série en cours ; parfait pour lancer la soutenance avec la classe

### T-43 · « Steam Wrapped » de l'année
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Samuel · **Due**: —
- **Origin**: idée fun pour la démo

- [ ] Page en cartes défilantes façon Spotify Wrapped : jeu de l'année, genre qui monte,
  plus grosse promo, plus gros flop, pays le plus cher

### T-44 · Ventes par région (Kaggle vgsales)
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Samuel · **Due**: —
- **Origin**: kaggle.com/datasets/gregorut/videogamesales

Pas spécifique à Steam ni au PC, mais la seule source de ventes par région.
- [ ] Genres préférés Amérique du Nord / Europe / Japon (barres groupées + mini-carte)
- [ ] Comparaison avec ce que donne notre carte n°2 (T-23)

### T-45 · Rafraîchissement automatique des données
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Antoine · **Due**: —
- **Origin**: T-09, T-21 (snapshots horaires)

- [ ] Planificateur (APScheduler ou `django-q2`) dans un conteneur `worker` de `compose.yml`
- [ ] Horaire : joueurs et Twitch ; quotidien : prix et avis ; mensuel : enquête matériel
- [ ] Page d'admin qui liste les derniers `ImportRun` et leurs erreurs

### T-46 · Thème Steam et mode sombre
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: S · **Owner**: Dorian · **Due**: —
- **Origin**: finition visuelle

- [ ] Palette sombre bleu-gris façon client Steam, mode clair en option
- [ ] Thème ECharts commun pour que tous les graphiques se ressemblent

### T-47 · Import Kaggle « Steam Reviews » (6 millions d'avis)
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: M · **Owner**: Nathan · **Due**: —
- **Origin**: kaggle.com/datasets/andrewmvd/steam-reviews

- [ ] Gros fichier : lecture en flux avec polars, n'importer que les agrégats + un
  échantillon de textes pour T-40
- [ ] Sentiment dans le temps par genre

### T-48 · GamerPower : jeux offerts en ce moment
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-23
- **Effort**: XS · **Owner**: Dorian · **Due**: —
- **Origin**: gamerpower.com/api/giveaways?platform=steam (sans clé)

- [ ] Encart « gratuit en ce moment » sur l'accueil

---

## ✅ Done

### Log

One line per closed ticket, most recent first:
`- **YYYY-MM-DD** · T-NN · Title — what was done (branch) · opened YYYY-MM-DD`.
