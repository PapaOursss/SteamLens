from django.db.models import DecimalField, OuterRef, Q, QuerySet, Subquery
from django.db.models.functions import Coalesce

from catalog.models import Game, ReviewSummary
from pricing.models import PricePoint

FRANCE_ISO2 = "FR"
ALL_LANGUAGES = "all"
# Au-delà, une erreur de source : le dataset Kaggle donne 707,84 $ à des jeux retirés de la
# vente (F1 2015, DiRT Rally). Les jeux les plus chers de Steam restent sous cette barre.
MAX_PLAUSIBLE_PRICE_EUR = 200


def priced_games(countries: tuple[str, ...] = (FRANCE_ISO2,)) -> QuerySet[Game]:
    """Jeux au prix et aux avis connus, annotés de `latest_price`, `positive` et `negative`.

    `latest_price` : le dernier prix en euros du premier pays de `countries` qui en a un.
    Prix connu : un prix relevé, ou gratuit d'après la page Steam lue. Le catalogue Kaggle
    marque des dizaines de milliers de jeux gratuits sans que leur page ait été lue : les
    compter ferait croire que Steam est surtout gratuit. Prix ou avis inconnus : le jeu est
    laissé de côté, jamais inventé.
    """
    prices = PricePoint.objects.filter(
        country__in=countries, price_eur__isnull=False, price_eur__lte=MAX_PLAUSIBLE_PRICE_EUR
    )
    latest_by_country = [
        Subquery(
            prices.filter(game=OuterRef("pk"), country=country)
            .order_by("-date")
            .values("price_eur")[:1]
        )
        for country in countries
    ]
    latest_review = ReviewSummary.objects.filter(
        game=OuterRef("pk"), language=ALL_LANGUAGES
    ).order_by("-date")
    # Le filtre passe avant les sous-requêtes : sinon elles tournent sur tout le catalogue.
    known_price = Q(appid__in=prices.values("game_id")) | Q(
        is_free=True, store_fetched_at__isnull=False
    )
    return (
        Game.objects.filter(known_price)
        .annotate(
            latest_price=Coalesce(*latest_by_country, None, output_field=DecimalField()),
            positive=Subquery(latest_review.values("positive")[:1]),
            negative=Subquery(latest_review.values("negative")[:1]),
        )
        .filter(positive__isnull=False)
    )
