from dataclasses import dataclass, field
from datetime import date
from typing import Any

from ingestion.sources.steam_store.release_date import parse_release_date
from ingestion.sources.steam_store.store_price import StorePrice


@dataclass(frozen=True)
class StoreAppDetails:
    """Fiche d'un jeu sur le Steam Store."""

    appid: int
    name: str
    app_type: str
    is_free: bool
    short_description: str
    header_image: str
    developers: list[str] = field(default_factory=list)
    publishers: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    screenshot_urls: list[str] = field(default_factory=list)
    minimum_requirements_html: str = ""
    metacritic_score: int | None = None
    release_date_text: str = ""
    release_date: date | None = None
    coming_soon: bool = False
    price: StorePrice | None = None

    @classmethod
    def from_data(cls, data: dict[str, Any], country_code: str) -> "StoreAppDetails":
        appid = int(data["steam_appid"])
        release = data.get("release_date") or {}
        price_overview = data.get("price_overview")
        return cls(
            appid=appid,
            name=data.get("name") or "",
            app_type=data.get("type") or "",
            is_free=bool(data.get("is_free")),
            short_description=data.get("short_description") or "",
            header_image=data.get("header_image") or "",
            developers=list(data.get("developers") or []),
            publishers=list(data.get("publishers") or []),
            genres=_descriptions(data.get("genres")),
            categories=_descriptions(data.get("categories")),
            platforms=[name for name, supported in (data.get("platforms") or {}).items() if supported],
            screenshot_urls=[shot["path_full"] for shot in data.get("screenshots") or []],
            minimum_requirements_html=_minimum_requirements(data.get("pc_requirements")),
            metacritic_score=(data.get("metacritic") or {}).get("score"),
            release_date_text=release.get("date") or "",
            release_date=parse_release_date(release.get("date") or ""),
            coming_soon=bool(release.get("coming_soon")),
            price=(
                StorePrice.from_price_overview(appid, country_code, price_overview)
                if price_overview
                else None
            ),
        )


def _descriptions(items: list[dict[str, Any]] | None) -> list[str]:
    return [item["description"] for item in items or []]


def _minimum_requirements(requirements: dict[str, str] | list | None) -> str:
    """Le Store renvoie une liste vide au lieu d'un objet quand il n'y a pas de configuration."""
    if not isinstance(requirements, dict):
        return ""
    return requirements.get("minimum", "")
