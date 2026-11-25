from rest_framework.pagination import PageNumberPagination

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


class PageSizePagination(PageNumberPagination):
    """Pagination par numéro de page ; `?page_size=` choisit la taille, plafonnée à 100."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE
