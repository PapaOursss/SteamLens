from rest_framework import serializers

from catalog.models import GameTag


class GameTagSerializer(serializers.ModelSerializer):
    """Tag d'un jeu avec son nombre de votes."""

    name = serializers.CharField(source="tag.name")

    class Meta:
        model = GameTag
        fields = ("name", "votes")
