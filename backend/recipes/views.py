from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.filters import RecipeFilter, IngredientSearchFilter
from recipes.models import (FavoriteRecipe,
                            Ingredient,
                            Recipe,
                            ShoppingCart,
                            Tag)
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (FavoriteRecipeSerializer,
                                 IngredientSerializer,
                                 RecipeCreateSerializer,
                                 RecipeSerializer,
                                 ShoppingCartSerializer,
                                 TagSerializer)
from recipes.utils import (download_txt,
                           get_ingredients_from_shopping_list)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс для обработки всех запросов, связанных с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс для обработки всех запросов, связанных с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для обработки всех запросов, связанных с рецептами."""
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.with_user_annotations(self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def _create_user_recipe_relations(self, serialiser, recipe_pk, request):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serialiser(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_user_recipe_relations(self, model, recipe_pk, request):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        deleted_count, _ = model.objects.filter(
            user=user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этого рецепта нет в вашем списке.'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self._create_user_recipe_relations(
            FavoriteRecipeSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._delete_user_recipe_relations(FavoriteRecipe, pk, request)

    @action(methods=('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self._create_user_recipe_relations(
            ShoppingCartSerializer, pk, request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._delete_user_recipe_relations(ShoppingCart, pk, request)

    @action(methods=('get',), detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/s/{recipe.short_code}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        self.permission_classes = (IsAuthenticated,)
        shopping_list = get_ingredients_from_shopping_list(request.user)
        return download_txt(shopping_list)


class RecipeShortLinkRedirectView(APIView):
    """
    Класс для обработки коротких ссылок на рецепты и
    и редиректа на нужный рецепт.
    """
    def get(self, request, short_code):
        recipe = get_object_or_404(
            Recipe, short_code=short_code)
        return redirect(f'/recipes/{recipe.id}/')
