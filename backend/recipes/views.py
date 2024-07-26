from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.serializers import ShortResipeSerializer
from recipes.filters import RecipeFilter, IngredientSearchFilter
from recipes.models import (Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            RecipeShortLink,
                            ShoppingCart,
                            Tag)
from recipes.permissions import IsAuthor
from recipes.serializers import (IngredientSerializer,
                                 RecipeSerializer,
                                 ShortLinkSerializer,
                                 TagSerializer)
from recipes.utils import (download_txt,
                           generate_unique_short_code,
                           get_ingredients_from_shopping_list)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action == ('shopping_cart', 'favorite',
                           'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ('partial_update', 'destroy'):
            self.permission_classes = (IsAuthor,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete'), detail=True)
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                errors = {
                    'errors': 'Этот рецепт уже есть в вашем списке избранного.'
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = ShortResipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            favorite_recipe = FavoriteRecipe.objects.filter(
                user=user, recipe=recipe)
            if not favorite_recipe:
                errors = {
                    'errors': 'Этого рецепта нет в списке ваших избранных.'
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete'), detail=True)
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            shopping_cart_item, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                errors = {
                    'errors': 'Этот рецепт уже есть в вашем списке покупок.'
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = ShortResipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            shopping_cart_item = ShoppingCart.objects.filter(
                user=user, recipe=recipe)
            if not shopping_cart_item:
                errors = {
                    'errors': 'Этого рецепта нет в вашем списке покупок.'
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            shopping_cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get',), detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link_obj, created = RecipeShortLink.objects.get_or_create(
            recipe=recipe)
        if created:
            short_code = generate_unique_short_code()
            short_link_obj.short_code = short_code
            short_link_obj.save()
        serializer = ShortLinkSerializer(short_link_obj,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        shopping_list = get_ingredients_from_shopping_list(request.user)
        return download_txt(shopping_list)


class RecipeShortLinkRedirectView(APIView):
    def get(self, request, short_code):
        short_link_obj = get_object_or_404(
            RecipeShortLink, short_code=short_code)
        recipe_id = short_link_obj.recipe.id
        return redirect(f'/recipes/{recipe_id}/')
