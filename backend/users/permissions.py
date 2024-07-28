from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserByPkOrAuthOnly(IsAuthenticatedOrReadOnly):
    """
    Класс для выдачи разрешения на доступ к эндпоинту users/me
    только авторизованным пользователям.
    """
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return super().has_permission(request, view)
