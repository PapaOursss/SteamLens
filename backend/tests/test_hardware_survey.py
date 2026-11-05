import datetime
from pathlib import Path

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from ingestion.http import ApiError
from ingestion.management.commands import import_hardware_survey
from ingestion.models import ImportRun
from ingestion.sources.steam_hwsurvey import SurveyClient, SurveyPageError, parse_survey
from players.models import HardwareShare

PAGE = Path(__file__).parent / "fixtures/steam_hwsurvey/survey_october_2026_extract.html"
OCTOBER = datetime.date(2026, 10, 1)


def survey_page() -> str:
    return PAGE.read_text(encoding="utf-8")


def test_the_page_gives_month_languages_and_systems() -> None:
    shares = {(share.category, share.item): share for share in parse_survey(survey_page())}
    assert shares["language", "Simplified Chinese"].percent == 21.98
    assert shares["os", "Linux"].percent == 3.95
    assert shares["os", "SteamOS Holo 64 bit"].percent == 0.55
    assert {share.month for share in shares.values()} == {OCTOBER}


def test_a_page_without_survey_is_rejected() -> None:
    with pytest.raises(SurveyPageError):
        parse_survey("<html>Welcome to Steam</html>")


@pytest.mark.django_db
def test_import_stores_the_month(monkeypatch: pytest.MonkeyPatch) -> None:
    client = SurveyClient(fetch_text=lambda url, params: survey_page())
    monkeypatch.setattr(import_hardware_survey, "build_client", lambda: client)

    call_command("import_hardware_survey")
    call_command("import_hardware_survey")

    linux = HardwareShare.objects.get(category="os", item="Linux")
    assert (linux.month, float(linux.percent)) == (OCTOBER, 3.95)
    assert ImportRun.objects.filter(source="steam_hwsurvey").count() == 2


@pytest.mark.django_db
def test_import_traces_a_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing(url: str, params: dict[str, str]) -> str:
        raise ApiError("steam_hwsurvey", url, "HTTP 503", 503)

    monkeypatch.setattr(import_hardware_survey, "build_client", lambda: SurveyClient(failing))
    call_command("import_hardware_survey")
    assert "503" in ImportRun.objects.get().errors


@pytest.mark.django_db
def test_hardware_survey_endpoint() -> None:
    september = datetime.date(2026, 9, 1)
    HardwareShare.objects.create(month=september, category="language", item="English", percent=40)
    HardwareShare.objects.create(month=OCTOBER, category="language", item="English", percent=39)
    HardwareShare.objects.create(
        month=OCTOBER, category="language", item="Simplified Chinese", percent=22
    )

    data = APIClient().get(reverse("stats-hardware-survey"), {"top": 1}).json()

    assert data["months"] == ["2026-09-01", "2026-10-01"]
    assert data["series"] == [{"item": "English", "values": [40.0, 39.0]}]
    assert data["highlights"][0]["values"] == [None, 22.0]
    bad = APIClient().get(reverse("stats-hardware-survey"), {"category": "nope"})
    assert bad.status_code == 400
