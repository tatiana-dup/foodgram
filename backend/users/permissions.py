from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserByPkOrAuthOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return super().has_permission(request, view)
