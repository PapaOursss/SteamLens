from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def health(request: Request) -> Response:
    """Répond si le backend tourne : sert au front et aux conteneurs."""
    return Response({"status": "ok"})
