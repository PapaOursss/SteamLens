import pytest
from django.core.management import get_commands

from ingestion.http.source_limits import min_interval_for
from ingestion.scheduling import SCHEDULE

NEW_IMPORTS = {
    "import_itad_history": "T-18",
    "import_reviews": "T-22",
    "import_hardware_survey": "T-27",
    "import_achievements": "T-35",
    "import_profile_countries": "T-37",
}


@pytest.mark.parametrize(("command", "ticket"), NEW_IMPORTS.items())
def test_each_import_exists_and_is_scheduled(command: str, ticket: str) -> None:
    assert command in get_commands()
    assert {(entry.command, entry.ticket) for entry in SCHEDULE} >= {(command, ticket)}


@pytest.mark.parametrize("source", ["steam_reviews", "isthereanydeal", "steam_hwsurvey"])
def test_new_sources_have_a_rate_limit(source: str) -> None:
    assert min_interval_for(source) >= 1.0
