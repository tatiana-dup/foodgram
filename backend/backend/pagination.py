from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

    # Нужен ли?
    # def paginate_queryset(self, queryset, request, view=None):
    #     if request.query_params:
    #         return None
    #     return super().paginate_queryset(queryset, request, view)
