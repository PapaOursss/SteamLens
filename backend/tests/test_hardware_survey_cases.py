import datetime

import httpx
import pytest
import respx
from django.urls import reverse
from rest_framework.test import APIClient

from ingestion.http import ApiError
from ingestion.sources.steam_hwsurvey import SurveyClient, SurveyPageError, parse_survey
from ingestion.sources.steam_hwsurvey.survey_client import SURVEY_URL, fetch_page
from ingestion.sources.steam_hwsurvey.survey_page import survey_month
from players.models import HardwareShare
from players.views_hardware import MAX_TOP

HEADER = "<h1>Steam Hardware &amp; Software Survey: March 2027</h1>"


def section(key: str, label: str, *rows: tuple[str, str]) -> str:
    details = "".join(
        f'<div class="stats_col_mid data_row"><nobr>{item}</nobr></div>\n'
        f'<div class="stats_col_right data_row">{percent}</div>\n'
        for item, percent in rows
    )
    return (
        f'<div class="stats_row row_0" id="{key}_stats_row">'
        f'<div class="stats_col_left">{label}</div></div>'
        f'<div class="stats_row_details" id="{key}_details">{details}</div>'
    )


def test_the_month_is_the_first_day() -> None:
    assert survey_month(HEADER) == datetime.date(2027, 3, 1)


def test_an_unknown_month_name_is_an_error() -> None:
    with pytest.raises(ValueError):
        survey_month("<h1>Steam Hardware & Software Survey: Brumaire 2027</h1>")


def test_untracked_categories_are_ignored() -> None:
    page = HEADER + section("cat1", "Free Hard Drive Space", ("100 GB", "10.00%"))
    assert parse_survey(page) == []


def test_html_entities_and_tags_are_cleaned() -> None:
    page = HEADER + section(
        "cat7", "Language", ("<strong>Portuguese &amp; Brazil</strong>", "<strong>4.20%</strong>")
    )
    share = parse_survey(page)[0]
    assert (share.category, share.item, share.percent) == ("language", "Portuguese & Brazil", 4.2)


def test_a_repeated_item_keeps_its_first_value() -> None:
    page = HEADER + section("osversion", "OS Version", ("Windows", "93.70%"), ("Windows", "1.00%"))
    assert [share.percent for share in parse_survey(page)] == [93.7]


def test_rows_without_percent_are_skipped() -> None:
    page = HEADER + section(
        "cat10", "VR Headsets", ("Valve Index HMD", ""), ("Meta Quest 3", "27.27%")
    )
    assert [share.item for share in parse_survey(page)] == ["Meta Quest 3"]


def test_a_section_without_details_gives_nothing() -> None:
    page = (
        HEADER
        + '<div class="stats_row" id="ram_stats_row"><div class="stats_col_left">System RAM</div></div>'
    )
    assert parse_survey(page) == []


def test_sections_do_not_bleed_into_each_other() -> None:
    page = (
        HEADER
        + section("cat7", "Language", ("English", "39.04%"))
        + section("cat10", "VR Headsets", ("Meta Quest 3", "27.27%"))
    )
    assert {(share.category, share.item) for share in parse_survey(page)} == {
        ("language", "English"), ("vr", "Meta Quest 3")
    }  # fmt: skip


def test_the_survey_page_error_is_a_value_error() -> None:
    assert issubclass(SurveyPageError, ValueError)


def test_the_client_asks_the_english_page() -> None:
    asked: list[tuple[str, dict[str, str]]] = []

    def fake(url: str, params: dict[str, str]) -> str:
        asked.append((url, params))
        return HEADER

    assert SurveyClient(fake).current_survey() == []
    assert asked == [(SURVEY_URL, {"l": "english"})]


@respx.mock
def test_fetch_page_returns_the_html() -> None:
    respx.get(SURVEY_URL).respond(text=HEADER)
    assert fetch_page(SURVEY_URL, {"l": "english"}) == HEADER


@respx.mock
def test_fetch_page_turns_http_errors_into_api_errors() -> None:
    respx.get(SURVEY_URL).respond(status_code=503)
    with pytest.raises(ApiError):
        fetch_page(SURVEY_URL, {})


@respx.mock
def test_fetch_page_turns_network_errors_into_api_errors() -> None:
    respx.get(SURVEY_URL).mock(side_effect=httpx.ConnectError("hors ligne"))
    with pytest.raises(ApiError, match="ConnectError"):
        fetch_page(SURVEY_URL, {})


def share(month: int, category: str, item: str, percent: float) -> None:
    HardwareShare.objects.create(month=datetime.date(2026, month, 1), category=category,
                                 item=item, percent=percent)  # fmt: skip


def get(**params: str) -> dict:
    return APIClient().get(reverse("stats-hardware-survey"), params).json()


def test_empty_survey(db: None) -> None:
    data = get()
    assert (data["category"], data["months"], data["series"]) == ("language", [], [])
    assert [highlight["values"] for highlight in data["highlights"]] == [[], [], []]


def test_top_items_come_from_the_latest_month(db: None) -> None:
    share(9, "os", "Windows", 95)
    share(9, "os", "Linux", 1)
    share(10, "os", "Linux", 96)
    share(10, "os", "Windows", 2)
    data = get(category="os", top="1")
    assert data["series"] == [{"item": "Linux", "values": [1.0, 96.0]}]


def test_months_are_shared_by_every_category(db: None) -> None:
    share(9, "gpu", "RTX", 5)
    share(10, "language", "English", 40)
    data = get(category="language")
    assert data["months"] == ["2026-09-01", "2026-10-01"]
    assert data["series"] == [{"item": "English", "values": [None, 40.0]}]


def test_top_is_capped(db: None) -> None:
    for index in range(MAX_TOP + 5):
        share(10, "gpu", f"GPU {index}", index)
    assert len(get(category="gpu", top="999")["series"]) == MAX_TOP


@pytest.mark.parametrize("top", ["-1", "abc", "2.5"])
def test_a_bad_top_is_refused(db: None, top: str) -> None:
    response = APIClient().get(reverse("stats-hardware-survey"), {"top": top})
    assert response.status_code == 400


def test_highlights_follow_linux_and_the_deck(db: None) -> None:
    share(10, "os", "Linux", 3.95)
    share(10, "os", "SteamOS Holo 64 bit", 0.55)
    labels = {row["label"]: row["values"] for row in get()["highlights"]}
    assert labels["Linux"] == [3.95]
    assert labels["Steam Deck (SteamOS Holo)"] == [0.55]
