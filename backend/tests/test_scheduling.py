import logging
from io import StringIO

import pytest
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

from ingestion.models import ImportRun
from ingestion.scheduling import SCHEDULE, add_jobs, run_scheduled_command


def test_every_scheduled_import_becomes_a_job() -> None:
    scheduler = BackgroundScheduler()

    add_jobs(scheduler, SCHEDULE)

    assert {job.id for job in scheduler.get_jobs()} == {entry.command for entry in SCHEDULE}


def test_list_option_prints_the_schedule() -> None:
    output = StringIO()

    call_command("run_scheduler", "--list", stdout=output)

    assert "snapshot_players (T-09)" in output.getvalue()


@pytest.mark.django_db
def test_a_command_not_written_yet_is_skipped(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        run_scheduled_command("import_from_nowhere")

    assert "import_from_nowhere sauté" in caplog.text
    assert not ImportRun.objects.exists()


@pytest.mark.django_db
def test_a_crashing_command_is_recorded_as_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def crash(command: str) -> None:
        raise RuntimeError("API en panne")

    monkeypatch.setattr("ingestion.scheduling.runner.call_command", crash)

    run_scheduled_command("run_scheduler")

    failed_run = ImportRun.objects.get()
    assert failed_run.source == "run_scheduler"
    assert not failed_run.succeeded
    assert "API en panne" in failed_run.errors
