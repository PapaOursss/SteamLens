from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlayerCount:
    """Nombre de joueurs connectés à un jeu à un instant donné (UTC)."""

    appid: int
    player_count: int
    counted_at: datetime
