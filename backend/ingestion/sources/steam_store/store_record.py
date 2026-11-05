import html
import re
from datetime import datetime

from ingestion.sources.steam_store.store_app_details import StoreAppDetails
from ingestion.writing import GameRecord

LINE_BREAK = re.compile(r"<br\s*/?>|</li>|</p>", re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")
BLANK_LINES = re.compile(r"\n\s*\n+")
PLATFORM_NAMES = {"windows": "Windows", "mac": "macOS", "linux": "Linux"}


def store_record(details: StoreAppDetails, fetched_at: datetime) -> GameRecord:
    """Traduit une fiche du Store en ligne à écrire (genres et plateformes en anglais)."""
    return GameRecord(
        appid=details.appid,
        name=details.name,
        fields={
            "is_free": details.is_free,
            "header_image": details.header_image,
            "short_description": html.unescape(details.short_description),
            "screenshots": details.screenshot_urls,
            "categories": details.categories,
            "minimum_requirements": requirements_text(details.minimum_requirements_html),
            "metacritic_score": details.metacritic_score,
            "release_date": details.release_date,
            "store_fetched_at": fetched_at,
        },
        genres=details.genres,
        developers=details.developers,
        publishers=details.publishers,
        platforms=[PLATFORM_NAMES.get(name, name) for name in details.platforms],
    )


def requirements_text(requirements_html: str) -> str:
    """La configuration minimale en texte simple, une ligne par élément."""
    text = TAG.sub("", LINE_BREAK.sub("\n", requirements_html))
    return BLANK_LINES.sub("\n", html.unescape(text)).strip()
