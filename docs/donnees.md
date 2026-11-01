# Modèle de données

L'**appid Steam** relie toutes les sources : chaque import retrouve son jeu par l'appid (IGDB,
RAWG et IsThereAnyDeal ont leur propre identifiant, rangé dans `Game`). Aucune donnée
personnelle : seulement des comptes par jeu, pays, langue ou date.

```mermaid
erDiagram
    Game ||--o{ GameTag : "tags votés"
    Tag ||--o{ GameTag : ""
    Game }o--o{ Genre : genres
    Game }o--o{ Theme : thèmes
    Game }o--o{ Genre : "genres IGDB"
    Game }o--o{ PlayerPerspective : "points de vue"
    Game ||--o{ IgdbPopularity : PopScore
    Game }o--o{ GameMode : modes
    Game }o--o{ Platform : plateformes
    Game }o--o{ Company : "développeurs / éditeurs"
    Company }o--o| Country : "pays du studio"
    Game ||--o{ PricePoint : prix
    Country ||--o{ PricePoint : ""
    Game ||--o{ PlayerCountSnapshot : "joueurs connectés"
    Game ||--o{ ReviewSummary : avis
    Game ||--o{ RankingEntry : classements

    Game {
        int appid PK
        string name
        date release_date
        bool is_free
        int igdb_id
        int rawg_id
        string itad_id
        int owners_min
        int owners_max
        int owners_mid
        int peak_ccu
        json supported_languages
        text short_description
        json screenshots
        json categories
        text minimum_requirements
        int metacritic_score
        datetime store_fetched_at
        date data_date
    }
    GameTag {
        int votes
    }
    Country {
        string iso2 PK
        string iso3
        string name_fr
        string continent
        string main_language
    }
    PricePoint {
        string currency
        decimal price
        decimal price_eur
        int discount_percent
        date date
        string source
    }
    PlayerCountSnapshot {
        datetime taken_at
        int players
        string source
    }
    ReviewSummary {
        string language
        int positive
        int negative
        date date
    }
    RankingEntry {
        string chart
        date date
        int rank
    }
    ImportRun {
        string source
        datetime started_at
        datetime finished_at
        int rows
        text errors
    }
```

| App | Modèles |
|---|---|
| `catalog` | `PlayerPerspective`, `IgdbPopularity` (PopScore IGDB), `ReviewExcerpt` (extraits d'avis anonymes, pour T-40), `Game`, `Genre`, `Tag`, `GameTag`, `Theme`, `GameMode`, `Platform`, `Company`, `ReviewSummary` |
| `geography` | `Country` (rempli par `geography.country_table.ensure_countries`), `RegionalSales` |
| `pricing` | `PricePoint` |
| `players` | `PlayerCountSnapshot`, `TwitchStreamSnapshot`, `RankingEntry` (top 100 SteamSpy) |
| `ingestion` | `ImportRun` (une ligne par import lancé : début, fin, lignes, erreurs) |

Les contraintes d'unicité (`GameTag` jeu + tag, `PricePoint` jeu + pays + date + source…)
rendent les imports idempotents : relancer un import met à jour au lieu de dupliquer.

## Écrire un import

Chaque source traduit ses réponses en `GameRecord` et les confie à
`ingestion.writing.GameWriter(data_date)` : paquets de 500, aucun doublon, liens (genres, tags,
studios, plateformes) ajoutés, votes de tags, temps de jeu et avis mis à jour. `data_date` est la
date des données : un jeu déjà rempli par une source plus récente ne voit que ses champs vides
comblés (« la donnée la plus récente gagne »). L'import s'enveloppe dans
`ingestion.import_tracking.tracked_import(source)`, qui remplit `ImportRun`.
