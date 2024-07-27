from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Класс для выдачи разрешений:
     - для неавторизованных пользователей доступны только безопасные методы;
     - для авторизованных доступны безопасные методы и создание объекта;
     - для авторов объекта доступны все запросы, в т.ч на изменение и удаление.
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
