Idée de visualisation : 
-	Evolution prix jeu 
-	Popularité des jeu (map interactive)
-	


Données : 
-	https://www.kaggle.com/datasets/trolukovich/steam-games-complete-dataset/data
-	https://www.igdb.com/
-	https://steamcommunity.com/dev 

Archi : 
-	Application web 
-	Règle gitHub et archi git 
-	Django (back), nuxt (vue.js), talewind, docker/podman
-	


DO :
-	Mettre wsl sur vscode via les double flèche ><
-	Faire un clone du projet dans ubuntu et pas en C :
-   Mettre en place un .venv 
    -   python3 -m venv .venv
    -   curl -LsSf https://astral.sh/uv/install.sh | sh
    -   déplace dans le backend
        - uv init 
            - si pas installer : sudo snap install astral-uv
    -   mettre fichier du venv dans le gitignore
-   Installer django 
-

Commandes :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # installer uv (Linux/WSL)
cd backend
uv init --python 3.13      # crée pyproject.toml et .python-version
uv add django               # crée .venv et installe Django
uv run django-admin startproject config .
uv run python manage.py runserver
```
