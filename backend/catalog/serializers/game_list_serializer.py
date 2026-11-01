from rest_framework import serializers

from catalog.models import Game


class GameListSerializer(serializers.ModelSerializer):
    """Ligne d'une liste de jeux : de quoi afficher une carte, rien de plus."""

    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Game
        fields = ("appid", "name", "release_date", "is_free", "header_image", "genres")
