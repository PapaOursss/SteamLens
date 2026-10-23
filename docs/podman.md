# Utiliser podman

Podman lance le projet dans des conteneurs : pas besoin d'installer Python ou Node sur son poste.

## Installer (une fois)

Ubuntu / WSL :

```bash
sudo apt update && sudo apt install -y podman podman-compose
podman --version     # vérifie que c'est installé
```

## Lancer le projet

Depuis la racine du repo :

```bash
podman compose up --build
```

- Frontend : http://localhost:3000
- Backend (API Django) : http://localhost:8000

Le code est partagé avec les conteneurs : une modification de fichier se voit tout de suite,
pas besoin de relancer. `Ctrl+C` arrête tout.

## Commandes du quotidien

| Je veux…                               | Commande                                                   |
| -------------------------------------- | ---------------------------------------------------------- |
| lancer en arrière-plan                 | `podman compose up -d`                                     |
| voir les logs                          | `podman compose logs -f backend` (ou `frontend`)           |
| arrêter                                | `podman compose down`                                      |
| reconstruire après un `uv add` / `npm install` | `podman compose up --build`                        |
| lancer une commande Django             | `podman compose exec backend uv run python manage.py <commande>` |
| créer une migration                    | `podman compose exec backend uv run python manage.py makemigrations` |
| ouvrir un terminal dans le conteneur   | `podman compose exec backend sh`                           |
| voir ce qui tourne                     | `podman ps`                                                |

## En cas de souci

- **Port déjà utilisé** : un `npm run dev` ou `runserver` tourne déjà ailleurs ; l'arrêter.
- **Ça marche plus après un changement de dépendances** : `podman compose down` puis
  `podman compose up --build`.
- **Tout remettre à zéro** : `podman compose down -v` puis `podman system prune -a`
  (supprime les images, il faudra tout retélécharger).
