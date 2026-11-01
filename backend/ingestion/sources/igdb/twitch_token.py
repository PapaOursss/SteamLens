import time
from collections.abc import Callable
from typing import Any

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
# On renouvelle un peu avant l'expiration annoncée, pour ne jamais envoyer un jeton périmé.
RENEWAL_MARGIN_SECONDS = 300

type TokenPoster = Callable[[str, dict[str, str]], Any]


class TwitchToken:
    """Jeton d'application Twitch (« client credentials »), qui ouvre aussi IGDB.

    Demandé à la première requête, renouvelé seul avant expiration ou sur demande (401).
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        post: TokenPoster,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.client_id = client_id
        self._client_secret = client_secret
        self._post = post
        self._clock = clock
        self._value = ""
        self._expires_at = 0.0

    def value(self) -> str:
        if not self._value or self._clock() >= self._expires_at:
            self.renew()
        return self._value

    def renew(self) -> None:
        body = self._post(
            TOKEN_URL,
            {
                "client_id": self.client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
            },
        )
        self._value = body["access_token"]
        self._expires_at = self._clock() + int(body["expires_in"]) - RENEWAL_MARGIN_SECONDS
