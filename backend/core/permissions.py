from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAuthenticatedOrRedirect(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        login_url = reverse('users:login') + '?next=' + request.path
        raise PermissionDenied(detail=redirect(login_url))
