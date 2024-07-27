from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all(),
                                             conjoined=False)
    is_favorited = filters.BooleanFilter(
        field_name='favorite_recipes', method='filter_by_boolean_field')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_cart', method='filter_by_boolean_field')

    def filter_by_boolean_field(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            filter_kwargs = {f'{name}__user': user}
            return queryset.filter(**filter_kwargs)
        else:
            filter_kwargs = {f'{name}__user': user}
            return queryset.exclude(**filter_kwargs)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
