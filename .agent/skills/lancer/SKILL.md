---
name: lancer
description: Lancer ou arrêter le projet SteamLens en local avec podman. À utiliser quand l'utilisateur veut démarrer, tester, voir le site, voir les logs ou arrêter le projet.
---

Depuis la racine du repo (détails : `docs/podman.md`) :

- Lancer : `podman compose up --build -d`, puis frontend http://localhost:3000,
  backend http://localhost:8000.
- Logs : `podman compose logs -f backend` (ou `frontend`).
- Commande Django : `podman compose exec backend uv run python manage.py <commande>`.
- Arrêter : `podman compose down`.

Port déjà utilisé : un autre serveur tourne déjà ; demander à l'utilisateur de l'arrêter.
Jamais `docker` ni `pip` : toujours `podman` et `uv`.
