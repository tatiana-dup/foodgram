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


class IngredientRecipeSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(min_value=1)

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }

    def validate_id(self, value):
        if Ingredient.objects.filter(pk=value).exists():
            return value
        raise serializers.ValidationError('Такого ингредиента не существует.')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('name', 'slug')

    def to_internal_value(self, data):
        if Tag.objects.filter(pk=data).exists():
            return {'id': data}
        raise serializers.ValidationError('Такого тега не существует.')


class RecipeSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializers(
        source='recipe_ingredients', many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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

    def validate_ingredients(self, value):
        return self._validate_many_to_many_field(value, 'ингредиент')

    def validate_tags(self, value):
        return self._validate_many_to_many_field(value, 'тег')

    def _validate_many_to_many_field(self, value, item_name):
        if not value:
            raise serializers.ValidationError(
                f'Укажите хотя бы один {item_name}.'
            )
        set_of_id = {item['id'] for item in value}
        if len(set(set_of_id)) != len(value):
            raise serializers.ValidationError(
                f'Каждый {item_name} должен быть указан один раз.'
            )
        return value

    def validate(self, attrs):
        errors = []
        if 'recipe_ingredients' not in attrs:
            errors.append({'error': 'Ингредиенты - обязательное поле.'})
        if 'tags' not in attrs:
            errors.append({'error': 'Теги - обязательное поле.'})
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        inrgedients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in inrgedients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        for tag in tags_data:
            RecipeTag.objects.create(
                recipe=recipe,
                tag_id=tag['id']
            )
        return recipe

    def update(self, instance, validated_data):
        inrgedients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.ingredients.clear()
        for ingredient in inrgedients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.clear()
        for tag in tags_data:
            RecipeTag.objects.create(
                recipe=instance,
                tag_id=tag['id']
            )
        instance.save()
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
