import logging
import traceback

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command, get_commands
from django.db import close_old_connections

from ingestion.models import ImportRun
from ingestion.scheduling.scheduled_command import ScheduledCommand

logger = logging.getLogger(__name__)

SCHEDULER_TIMEZONE = "Europe/Paris"


def run_scheduled_command(command: str) -> None:
    """Lance une commande d'import ; un plantage est tracé dans `ImportRun`, sans tout arrêter."""
    if command not in get_commands():
        logger.warning("Import %s sauté : la commande n'existe pas encore.", command)
        return
    close_old_connections()
    try:
        call_command(command)
    except Exception:
        logger.exception("Import %s en échec.", command)
        ImportRun.objects.create(source=command).finish(rows=0, errors=traceback.format_exc())


def add_jobs(scheduler: BaseScheduler, schedule: tuple[ScheduledCommand, ...]) -> None:
    for entry in schedule:
        scheduler.add_job(
            run_scheduled_command,
            CronTrigger.from_crontab(entry.cron, timezone=SCHEDULER_TIMEZONE),
            args=(entry.command,),
            id=entry.command,
            name=f"{entry.command} ({entry.ticket})",
            coalesce=True,
            max_instances=1,
        )
