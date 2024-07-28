from django.db import transaction
from rest_framework import serializers, validators

from common.serializers import Base64ImageField, ShortResipeSerializer
from recipes.models import (Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.serializers import AppUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации об ингредиентах."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializers(serializers.ModelSerializer):
    """
    Сериализатор для чтения информации об ингредиентах, добавленных в
    определенном количестве в рецепт.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsAddSerialazer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о тэгах."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о рецептах."""
    author = AppUserSerializer()
    ingredients = IngredientRecipeSerializers(
        source='recipe_ingredients', many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        return self._check_user_relation(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self._check_user_relation(obj, ShoppingCart)

    def _check_user_relation(self, obj, model):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return model.objects.filter(user=request.user, recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""
    author = AppUserSerializer(read_only=True)
    ingredients = IngredientsAddSerialazer(many=True)
    image = Base64ImageField()
    tags = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all()),
        allow_empty=False
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент.'
            )
        set_of_id = {item['id'] for item in value}
        if len(set_of_id) != len(value):
            raise serializers.ValidationError(
                'Каждый ингредиент должен быть указан один раз.'
            )
        return value

    def validate_tags(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError(
                'Каждый тег должен быть указан один раз.'
            )
        return value

    def validate(self, attrs):
        errors = []
        if 'ingredients' not in attrs:
            errors.append({'error': 'Ингредиенты - обязательное поле.'})
        if 'tags' not in attrs:
            errors.append({'error': 'Теги - обязательное поле.'})
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def _add_ingredients_to_recipe(self, recipe, ingredients_list):
        for ingredient in ingredients_list:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @transaction.atomic
    def create(self, validated_data):
        inrgedients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self._add_ingredients_to_recipe(recipe, inrgedients_data)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        inrgedients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self._add_ingredients_to_recipe(instance, inrgedients_data)
        instance.tags.set(tags)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class UserRecipeBaseSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для создания отношений между рецептом и пользователем.
    """
    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortResipeSerializer(instance.recipe).data


class FavoriteRecipeSerializer(UserRecipeBaseSerializer):
    """Сериализатор для добавления рецепта в избранное."""
    class Meta(UserRecipeBaseSerializer.Meta):
        model = FavoriteRecipe
        validators = [
            validators.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже есть в вашем списке избранного.'
            )
        ]


class ShoppingCartSerializer(UserRecipeBaseSerializer):
    """Сериализатор для добавления рецепта в список покупок."""
    class Meta(UserRecipeBaseSerializer.Meta):
        model = ShoppingCart
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже есть в вашем списке покупок.'
            )
        ]
