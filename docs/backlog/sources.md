# Vue d'ensemble

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


