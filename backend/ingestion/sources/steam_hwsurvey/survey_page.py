"""Lecture de la page publique de l'enquête matériel et logiciels de Steam (T-27)."""

import html
import re
from datetime import date, datetime

from ingestion.sources.steam_hwsurvey.survey_share import SurveyShare

# Libellé de la page (en anglais, `?l=english`) → catégorie enregistrée.
CATEGORIES = {
    "OS Version": "os",
    "System RAM": "ram",
    "Video Card Description": "gpu",
    "Language": "language",
    "VR Headsets": "vr",
}
MONTH_PATTERN = re.compile(r"Software Survey:\s*([A-Z][a-z]+ \d{4})")
SECTION_PATTERN = re.compile(
    r'id="(\w+)_stats_row".*?<div class="stats_col_left">([^<]+)</div>', re.DOTALL
)
ROW_PATTERN = re.compile(
    r'<div class="stats_col_mid data_row">(.*?)</div>\s*'
    r'<div class="stats_col_right data_row">(.*?)</div>',
    re.DOTALL,
)
TAG_PATTERN = re.compile(r"<[^>]+>")


class SurveyPageError(ValueError):
    """La page ne ressemble plus à l'enquête attendue (Steam a changé sa mise en page)."""


def survey_month(page: str) -> date:
    match = MONTH_PATTERN.search(page)
    if match is None:
        raise SurveyPageError("mois de l'enquête introuvable")
    return datetime.strptime(match.group(1), "%B %Y").date()


def parse_survey(page: str) -> list[SurveyShare]:
    """Toutes les lignes des catégories suivies, pour le mois affiché par la page."""
    month = survey_month(page)
    shares = []
    for key, label in SECTION_PATTERN.findall(page):
        category = CATEGORIES.get(html.unescape(label).strip())
        if category is not None:
            shares.extend(
                SurveyShare(month=month, category=category, item=item, percent=percent)
                for item, percent in _rows(_details(page, key))
            )
    return shares


def _details(page: str, key: str) -> str:
    start = page.find(f'id="{key}_details"')
    if start < 0:
        return ""
    end = page.find('_stats_row"', start)
    return page[start : end if end > 0 else len(page)]


def _rows(details: str) -> list[tuple[str, float]]:
    rows = {}
    for raw_item, raw_percent in ROW_PATTERN.findall(details):
        item = html.unescape(TAG_PATTERN.sub("", raw_item)).strip()
        percent = TAG_PATTERN.sub("", raw_percent).strip().rstrip("%")
        if item and percent:
            rows.setdefault(item, float(percent))
    return list(rows.items())
