from rest_framework import serializers

from catalog.models import Game
from catalog.serializers.game_tag_serializer import GameTagSerializer


class GameDetailSerializer(serializers.ModelSerializer):
    """Fiche complète d'un jeu : listes de référence aplaties en noms."""

    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    tags = GameTagSerializer(source="game_tags", many=True, read_only=True)
    themes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    game_modes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    platforms = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    developers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    publishers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Game
        fields = (
            "appid",
            "name",
            "release_date",
            "is_free",
            "header_image",
            "genres",
            "tags",
            "themes",
            "game_modes",
            "platforms",
            "developers",
            "publishers",
        )
