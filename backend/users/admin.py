from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import AppUser


admin.site.unregister(Group)


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

    search_fields = ('username', 'email', 'first_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Информация о пользователе', {
            'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
