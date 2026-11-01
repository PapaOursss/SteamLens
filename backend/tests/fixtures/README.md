# Fixtures des API

Vraies réponses des API, enregistrées une fois (le 2026-10-23) pour que les tests tournent
**sans réseau** : un test sert le fichier avec `respx` au lieu d'appeler l'API.

```python
from tests.fixture_files import load_fixture

respx.get(STEAMSPY_URL).respond(json=load_fixture("steamspy_appdetails_413150"))
```

| Fichier | Requête |
|---|---|
| `steamspy_appdetails_413150.json` | `steamspy.com/api.php?request=appdetails&appid=413150` |
| `steam_store_appdetails_413150_fr.json` | `store.steampowered.com/api/appdetails?appids=413150&cc=fr&l=french&filters=basic,price_overview,genres,release_date,developers,publishers,platforms` |
| `steam_store_price_413150_us.json` | `store.steampowered.com/api/appdetails?appids=413150&cc=us&filters=price_overview` |
| `cheapshark_games_413150.json` | `cheapshark.com/api/1.0/games?steamAppID=413150` |
| `frankfurter_latest_eur.json` | `api.frankfurter.dev/v1/latest?base=EUR&symbols=USD,GBP,BRL,TRY,JPY` |

Ajouter une source : enregistrer sa réponse ici (`curl … -o`, puis indenter), sans clé d'API
ni donnée personnelle dedans, et l'ajouter au tableau. Les sources à clé (Steam Web API,
IGDB, Twitch, RAWG, IsThereAnyDeal) s'ajoutent quand la clé existe (`docs/backlog/urgent.md`).
