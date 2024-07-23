from django.contrib.auth import get_user_model
from django.db import models

from recipes.constants import (INGREDIENT_MEASUREMENT_UNIT_MAX_LENGHT,
                               INGREDIENT_NAME_MAX_LENGHT,
                               RECIPE_NAME_MAX_LENGHT,
                               TAG_NAME_MAX_LENGHT,
                               TAG_SLUG_MAX_LENGHT,
                               TEXT_MAX_LENGHT_FOR_ADMIN_ZONE)
from recipes.validators import validate_cooking_time


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_MAX_LENGHT, unique=True,)
    slug = models.SlugField(
        'Слаг', max_length=TAG_SLUG_MAX_LENGHT, unique=True, null=True)

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
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Тэги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:TEXT_MAX_LENGHT_FOR_ADMIN_ZONE]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиенты')
    amount = models.IntegerField(verbose_name='Количество')

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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тэги')

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги рецепта'

    def __str__(self):
        return f'{self.recipe} в категории {self.tag}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class RecipeShortLink(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE)
    short_code = models.CharField(max_length=6, unique=True)
