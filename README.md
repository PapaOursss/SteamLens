# SteamLens

Application web de visualisation de données Steam (évolution des prix, popularité des jeux).
Backend Django (Python, géré par uv), frontend Nuxt + Tailwind.

## Prérequis

- Linux ou WSL (cloner le projet dans le système de fichiers Ubuntu, pas sous `C:`).
- [git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/) :

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- [kiln](https://github.com/antoine-tena/kiln) (facultatif) : outillage qui installe et lance le
  projet en une commande.

## Télécharger le projet

```bash
git clone https://github.com/PapaOursss/SteamLens.git
cd SteamLens
```

## Lancer avec uv

```bash
cd backend
uv sync                              # crée .venv et installe les dépendances (Python compris)
uv run python manage.py migrate      # prépare la base de données
uv run python manage.py runserver    # http://127.0.0.1:8000
```

`uv run` utilise toujours l'environnement du projet : pas besoin d'activer le `.venv`.
Pour ajouter une dépendance : `uv add <paquet>`.

## Lancer avec kiln

```bash
kiln install    # prépare le poste après le clone (dépendances, outils, hooks)
kiln dev        # lance le projet en local (backend et frontend)
kiln check      # lance les contrôles (tests, lint, typage)
```

`kiln dev --containers` lance toute la pile dans podman. `kiln doctor` diagnostique le poste
et donne les correctifs.
