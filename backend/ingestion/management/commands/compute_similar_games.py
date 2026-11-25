from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Game, GameMapPoint, SimilarGame
from catalog.similarity import TagMatrix, build_tag_matrix, nearest_neighbours, project_to_plane
from ingestion.import_tracking import tracked_import

SOURCE = "similar_games"
# Au-delà, le nuage de points devient illisible et t-SNE prend plusieurs minutes.
DEFAULT_MAP_SIZE = 3000


class Command(BaseCommand):
    help = "Jeux similaires par tags (10 voisins par jeu) et carte 2D du catalogue (T-41)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--map-size", type=int, default=DEFAULT_MAP_SIZE,
            help="jeux les plus possédés placés sur la carte",
        )  # fmt: skip

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            matrix = build_tag_matrix()
            if not matrix.appids:
                report.add_error("Aucun jeu avec assez de tags : lancer d'abord import_steamspy.")
            report.rows += save_neighbours(matrix)
            report.rows += save_map(options["map_size"])
        self.stdout.write(f"Jeux similaires : {report.rows} lignes écrites.")


@transaction.atomic
def save_neighbours(matrix: TagMatrix) -> int:
    links = [
        SimilarGame(game_id=appid, similar_id=similar, rank=rank, score=score)
        for appid, neighbours in nearest_neighbours(matrix).items()
        for rank, (similar, score) in enumerate(neighbours, start=1)
    ]
    SimilarGame.objects.all().delete()
    SimilarGame.objects.bulk_create(links)
    return len(links)


@transaction.atomic
def save_map(size: int) -> int:
    most_owned = list(
        Game.objects.filter(owners_mid__isnull=False)
        .order_by("-owners_mid", "appid")
        .values_list("appid", flat=True)
    )
    matrix = build_tag_matrix(most_owned).head(size)
    coordinates = project_to_plane(matrix)
    points = [
        GameMapPoint(game_id=appid, x=float(coordinates[row][0]), y=float(coordinates[row][1]),
                     main_tag_id=matrix.main_tag(row))
        for row, appid in enumerate(matrix.appids)
    ]  # fmt: skip
    GameMapPoint.objects.all().delete()
    GameMapPoint.objects.bulk_create(points)
    return len(points)
