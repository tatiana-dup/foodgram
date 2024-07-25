from rest_framework import serializers

from common.serializers import Base64ImageField
from recipes.models import (Ingredient,
                            FavoriteRecipe,
                            Recipe,
                            RecipeIngredient,
                            RecipeShortLink,
                            RecipeTag,
                            ShoppingCart,
                            Tag)
from users.serializers import MyUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')


class IngredientsAddSerialazer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'Такого ингредиента не существует.')
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializers(
        source='recipe_ingredients', many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
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


def validate_tag(value):
    if not Tag.objects.filter(pk=value).exists():
        raise serializers.ValidationError('Такого тэга не существует')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientsAddSerialazer(many=True)
    image = Base64ImageField()
    tags = serializers.ListField(
        child=serializers.IntegerField(
            min_value=0, validators=(validate_tag,)),
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

    def create(self, validated_data):
        inrgedients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in inrgedients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        for tag in tags:
            RecipeTag.objects.create(
                recipe=recipe,
                tag_id=tag
            )
        return recipe

    def update(self, instance, validated_data):
        inrgedients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in inrgedients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.save
        return instance


class ShortLinkSerializer(serializers.ModelSerializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = RecipeShortLink
        fields = ('short_link',)

    def get_short_link(self, obj):
        request = self.context['request']
        short_code = obj.short_code
        return request.build_absolute_uri(f'/s/{short_code}/')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['short-link'] = representation.pop('short_link')
        return representation
