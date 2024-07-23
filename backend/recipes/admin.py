from django.contrib import admin

from recipes.models import (Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            RecipeIngredient,
                            RecipeTag,
                            Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    autocomplete_fields = ('ingredient',)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0
    autocomplete_fields = ('tag',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('number_of_favorites_added', 'pub_date')
    list_display = ('name', 'author', 'number_of_favorites_added')
    list_display_links = ('name',)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def has_add_permission(self, request):
        return False

    @admin.display(description='Добавлений в избранное:')
    def number_of_favorites_added(self, instance):
        return FavoriteRecipe.objects.filter(recipe=instance).count()
