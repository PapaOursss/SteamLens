from argparse import ArgumentParser

from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand

from ingestion.scheduling import SCHEDULE, SCHEDULER_TIMEZONE, add_jobs


class Command(BaseCommand):
    help = "Lance le planificateur des imports (conteneur worker) ; --list affiche le planning."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--list", action="store_true", help="affiche le planning et sort")

    def handle(self, *args: object, **options: object) -> None:
        if options["list"]:
            for entry in SCHEDULE:
                self.stdout.write(f"{entry.cron:<12} {entry.command} ({entry.ticket})")
            return
        scheduler = BlockingScheduler(timezone=SCHEDULER_TIMEZONE)
        add_jobs(scheduler, SCHEDULE)
        self.stdout.write(f"Planificateur lancé : {len(SCHEDULE)} imports planifiés.")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
