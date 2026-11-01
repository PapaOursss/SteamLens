"""Petits nettoyages communs aux CSV Kaggle : listes, dates, montants."""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

DATE_FORMATS = ("%b %d, %Y", "%d %b, %Y", "%B %d, %Y", "%d %B, %Y", "%Y-%m-%d", "%b %Y", "%Y")
MONEY = re.compile(r"\d[\d,]*(?:\.\d+)?")
FREE_WORDS = ("free",)


def split_list(text: str | None, separator: str = ",") -> list[str]:
    if not text:
        return []
    return [item.strip() for item in text.split(separator) if item.strip()]


def parse_date(text: str | None) -> date | None:
    """« May 12, 2016 », « 12 May, 2016 », « Jan 2019 »… ; None si vague ou illisible."""
    cleaned = (text or "").strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, date_format).date()
        except ValueError:
            continue
    return None


def parse_money(text: str | None) -> Decimal | None:
    """« $19.99 » → 19.99, « Free to Play » → 0, texte sans montant → None."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    if cleaned.lower().startswith(FREE_WORDS):
        return Decimal(0)
    match = MONEY.search(cleaned)
    if match is None:
        return None
    try:
        return Decimal(match.group().replace(",", ""))
    except InvalidOperation:
        return None


def parse_int(text: str | None) -> int | None:
    try:
        return int(float((text or "").strip()))
    except ValueError:
        return None


def latest_date(dates: list[date | None], ceiling: date) -> date:
    """Date des données d'un dataset : la plus récente sortie qu'il contient (bornée à aujourd'hui)."""
    known = [day for day in dates if day is not None and day <= ceiling]
    return max(known, default=ceiling)
