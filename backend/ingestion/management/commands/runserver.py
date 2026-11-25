import os

from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from django.core.management import call_command


class Command(RunserverCommand):
    help = "Prépare la base (données et migrations), puis lance le serveur."

    def handle(self, *args: object, **options: object) -> None:
        # RUN_MAIN : processus relancé à chaque modification du code, la base est déjà prête.
        if os.environ.get("RUN_MAIN") != "true":
            call_command("prepare_database")
        super().handle(*args, **options)
