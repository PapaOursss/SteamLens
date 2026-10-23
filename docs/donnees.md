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
    Game }o--o{ GameMode : modes
    Game }o--o{ Platform : plateformes
    Game }o--o{ Company : "développeurs / éditeurs"
    Company }o--o| Country : "pays du studio"
    Game ||--o{ PricePoint : prix
    Country ||--o{ PricePoint : ""
    Game ||--o{ PlayerCountSnapshot : "joueurs connectés"
    Game ||--o{ ReviewSummary : avis

    Game {
        int appid PK
        string name
        date release_date
        bool is_free
        int igdb_id
        int rawg_id
        string itad_id
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
| `catalog` | `Game`, `Genre`, `Tag`, `GameTag`, `Theme`, `GameMode`, `Platform`, `Company`, `ReviewSummary` |
| `geography` | `Country` |
| `pricing` | `PricePoint` |
| `players` | `PlayerCountSnapshot` |
| `ingestion` | `ImportRun` (une ligne par import lancé : début, fin, lignes, erreurs) |

Les contraintes d'unicité (`GameTag` jeu + tag, `PricePoint` jeu + pays + date + source…)
rendent les imports idempotents : relancer un import met à jour au lieu de dupliquer.
