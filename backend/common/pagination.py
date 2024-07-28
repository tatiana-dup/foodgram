from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    Класс для пагинации, на основе limit, который может быть
    передан в параметрах запроса. limit задает количество рецептов на странице.
    """
    page_size_query_param = 'limit'
