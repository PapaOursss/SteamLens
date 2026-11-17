from rest_framework import serializers

from catalog.models import Game
from catalog.serializers.game_tag_serializer import GameTagSerializer
from ingestion.writing.game_writer import ALL_LANGUAGES

PERCENT = 100


class GameDetailSerializer(serializers.ModelSerializer):
    """Fiche complète d'un jeu : listes de référence aplaties en noms."""

    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    tags = GameTagSerializer(source="game_tags", many=True, read_only=True)
    themes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    game_modes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    platforms = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    developers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    publishers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    positive_share = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "appid",
            "name",
            "release_date",
            "is_free",
            "header_image",
            "short_description",
            "metacritic_score",
            "positive_share",
            "genres",
            "tags",
            "themes",
            "game_modes",
            "platforms",
            "developers",
            "publishers",
        )

    def get_positive_share(self, game: Game) -> int | None:
        """Part d'avis positifs, toutes langues, au dernier relevé ; None sans avis."""
        latest = game.reviews.filter(language=ALL_LANGUAGES).order_by("-date").first()
        if latest is None or not latest.total:
            return None
        return round(latest.positive * PERCENT / latest.total)
