from rest_framework import serializers

from pricing.models import PricePoint


class PricePointSerializer(serializers.ModelSerializer):
    """Un point de la courbe des prix, dans un pays."""

    country = serializers.CharField(source="country_id")

    class Meta:
        model = PricePoint
        fields = ("date", "country", "currency", "price", "price_eur", "discount_percent", "source")
