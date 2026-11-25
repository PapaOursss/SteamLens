from django.core.management.base import BaseCommand

from catalog.views.streamgraph import load_streamgraph
from catalog.views.tag_network import load_tag_network
from catalog.views.treemap import load_treemap


class Command(BaseCommand):
    help = "Calcule d'avance les statistiques lentes ; ne refait rien si le catalogue est le même."

    def handle(self, *args: object, **options: object) -> None:
        for load in (load_treemap, load_tag_network, load_streamgraph):
            load()
        self.stdout.write("Statistiques lentes prêtes.")
