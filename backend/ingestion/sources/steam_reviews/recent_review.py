from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RecentReview:
    """Un avis récent réduit au strict nécessaire.

    `author_steamid` ne vit qu'en mémoire, le temps de demander le pays du profil (T-37) :
    aucun import ne l'écrit en base ni sur le disque.
    """

    created_at: datetime
    voted_up: bool
    author_steamid: str
