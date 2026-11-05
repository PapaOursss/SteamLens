from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ingestion.sources.steamspy.owners_range import OwnersRange

CENTS_PER_UNIT = 100
LIST_SEPARATOR = ","


@dataclass(frozen=True)
class SteamSpyGame:
    """Un jeu tel que SteamSpy le décrit, prix en dollars US."""

    appid: int
    name: str
    developer: str
    publisher: str
    owners: OwnersRange
    positive_reviews: int
    negative_reviews: int
    average_playtime_minutes: int
    median_playtime_minutes: int
    concurrent_users: int
    price_usd: Decimal | None
    initial_price_usd: Decimal | None
    discount_percent: int
    languages: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    tag_votes: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SteamSpyGame":
        return cls(
            appid=int(payload["appid"]),
            name=payload.get("name") or "",
            developer=payload.get("developer") or "",
            publisher=payload.get("publisher") or "",
            owners=OwnersRange.from_text(payload["owners"]),
            positive_reviews=int(payload.get("positive") or 0),
            negative_reviews=int(payload.get("negative") or 0),
            average_playtime_minutes=int(payload.get("average_forever") or 0),
            median_playtime_minutes=int(payload.get("median_forever") or 0),
            concurrent_users=int(payload.get("ccu") or 0),
            price_usd=_cents_to_units(payload.get("price")),
            initial_price_usd=_cents_to_units(payload.get("initialprice")),
            discount_percent=int(payload.get("discount") or 0),
            languages=_split_list(payload.get("languages")),
            genres=_split_list(payload.get("genre")),
            tag_votes=_parse_tags(payload.get("tags")),
        )


def _cents_to_units(cents: str | int | None) -> Decimal | None:
    if cents is None or cents == "":
        return None
    return Decimal(int(cents)) / CENTS_PER_UNIT


def _split_list(text: str | None) -> list[str]:
    if not text:
        return []
    return [item.strip() for item in text.split(LIST_SEPARATOR) if item.strip()]


def _parse_tags(tags: dict[str, int] | list | None) -> dict[str, int]:
    """SteamSpy renvoie une liste vide au lieu d'un objet quand le jeu n'a aucun tag."""
    if not isinstance(tags, dict):
        return {}
    return {name: int(votes) for name, votes in tags.items()}
