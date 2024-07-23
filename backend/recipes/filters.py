from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


# def filter_is_favorited(self, queryset, name, value, field_name):
#     user = self.request.user
#     if not user.is_authenticated:
#         return queryset
#     if value is True:
#         return queryset.filter(favoriterecipe__user=user)
#     else:
#         return queryset.exclude(favoriterecipe__user=user)


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author_id')
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all(),
                                             conjoined=False)
    is_favorited = filters.BooleanFilter(
        field_name='favoriterecipe', method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppingcart_set', method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value is True:
            return queryset.filter(favoriterecipe__user=user)
        else:
            return queryset.exclude(favoriterecipe__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value is True:
            return queryset.filter(shoppingcart__user=user)
        else:
            return queryset.exclude(shoppingcart__user=user)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
