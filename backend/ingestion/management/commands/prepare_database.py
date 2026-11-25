from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import OperationalError, connection

from catalog.models import Game
from ingestion.shared_database import SharedDatabaseError, install_shared_database


def has_games() -> bool:
    if Game._meta.db_table not in connection.introspection.table_names():
        return False
    try:
        return Game.objects.exists()
    except OperationalError:
        # Table d'une version plus ancienne : elle contient peut-être des données, on la garde.
        return True


class Command(BaseCommand):
    help = "Télécharge la base partagée si la base locale est vide, puis applique les migrations."

    def handle(self, *args: object, **options: object) -> None:
        if not has_games():
            self.download()
        call_command("migrate", verbosity=0)

    def download(self) -> None:
        self.stdout.write("Base vide : téléchargement de la base partagée (126 Mo)…")
        connection.close()
        try:
            install_shared_database(Path(connection.settings_dict["NAME"]))
        except SharedDatabaseError as error:
            self.stderr.write(f"Base partagée non installée ({error}) : démarrage sans données.")
        else:
            self.stdout.write("Base partagée installée.")
