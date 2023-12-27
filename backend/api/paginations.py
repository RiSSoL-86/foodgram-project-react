from foodgram.settings import DEFAULT_PAGES_LIMIT
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомная пагинация для Рецептов и Пользователей."""
    page_size_query_param = "limit"
    page_size = DEFAULT_PAGES_LIMIT