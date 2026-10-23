from rest_framework import serializers

from players.models import PlayerCountSnapshot


class PlayerCountSerializer(serializers.ModelSerializer):
    """Un point de la courbe des joueurs connectés."""

    class Meta:
        model = PlayerCountSnapshot
        fields = ("taken_at", "players", "source")
