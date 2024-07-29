from django.db.models import QuerySet, Exists, OuterRef, Value, BooleanField


class RecipeQuerySet(QuerySet):
    def with_user_annotations(self, user):
        # Не уверена, что это хорошая практика для импорта, но иначе получается
        # циклический импорт: из моделей сюда, и в модели отсюда.
        from recipes.models import FavoriteRecipe, ShoppingCart
        if user.is_authenticated:
            return self.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                )
            )
        return self.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField())
        )
