import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (CODE_FOR_RECIPE_SHORT_LINK_MAX_LENGTH,
                               INGREDIENT_MEASUREMENT_UNIT_MAX_LENGHT,
                               INGREDIENT_NAME_MAX_LENGHT,
                               RECIPE_NAME_MAX_LENGHT,
                               TAG_NAME_MAX_LENGHT,
                               TAG_SLUG_MAX_LENGHT,
                               TEXT_MAX_LENGHT_FOR_ADMIN_ZONE)
from recipes.querysets import RecipeQuerySet
from recipes.validators import validate_cooking_time


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_MAX_LENGHT, unique=True,)
    slug = models.SlugField(
        'Слаг', max_length=TAG_SLUG_MAX_LENGHT, unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENT_NAME_MAX_LENGHT)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGHT)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        'Название', max_length=RECIPE_NAME_MAX_LENGHT)
    image = models.ImageField(
        'Фото', upload_to='recipes/images')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        help_text='Время в минутах',
        validators=(validate_cooking_time,))
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes')
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэги',
        related_name='recipes')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    short_code = models.CharField(
        max_length=CODE_FOR_RECIPE_SHORT_LINK_MAX_LENGTH,
        unique=True, blank=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:TEXT_MAX_LENGHT_FOR_ADMIN_ZONE]

    def generate_unique_short_code(self):
        while True:
            short_code = ''.join(random.choices(
                string.ascii_letters + string.digits,
                k=CODE_FOR_RECIPE_SHORT_LINK_MAX_LENGTH))
            if not Recipe.objects.filter(short_code=short_code).exists():
                return short_code

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_unique_short_code()
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='recipe_ingredients')
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(1, 'Укажите количество больше 0.'),))

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты для рецепта'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags')
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэги',
        related_name='recipe_tags')

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги рецепта'

    def __str__(self):
        return f'{self.recipe} в категории {self.tag}'


class UserRecipeBase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)

    class Meta:
        abstract = True


class FavoriteRecipe(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'favorite_recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_favorite_recipe'),
        )


class ShoppingCart(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_in_cart'),
        )
