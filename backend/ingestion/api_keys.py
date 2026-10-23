import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def get_api_keys(source: str, *names: str) -> dict[str, str] | None:
    """Renvoie les clés demandées, ou None (avec un message clair) s'il en manque une.

    Une commande d'import qui reçoit None saute sa source au lieu de planter.
    """
    keys = {name: settings.API_KEYS.get(name, "") for name in names}
    missing = [name for name, value in keys.items() if not value]
    if missing:
        logger.warning(
            "Source %s sautée : %s absente(s) de backend/.env (voir backend/.env.example).",
            source,
            ", ".join(missing),
        )
        return None
    return keys
