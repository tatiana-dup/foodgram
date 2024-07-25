import random
import string

from django.http import HttpResponse

from recipes.constants import CODE_FOR_RECIPE_SHORT_LINK_MAX_LENGTH
from recipes.models import (Ingredient,
                            RecipeIngredient,
                            RecipeShortLink)


def generate_unique_short_code():
    while True:
        short_code = ''.join(random.choices(
            string.ascii_letters + string.digits,
            k=CODE_FOR_RECIPE_SHORT_LINK_MAX_LENGTH))
        if not RecipeShortLink.objects.filter(short_code=short_code).exists():
            return short_code


def get_ingredients_from_shopping_list(user):
    recipe_ids = user.shopping_cart.values_list('recipe_id', flat=True)
    ingredients_list = RecipeIngredient.objects.filter(
        recipe_id__in=recipe_ids).values('ingredient_id', 'amount')
    ingred_dict = {}
    for item in ingredients_list:
        ingred_id = item['ingredient_id']
        amount = item['amount']
        if ingred_id in ingred_dict:
            amount = amount + ingred_dict[ingred_id]
        ingred_dict[ingred_id] = amount
    ingredients = Ingredient.objects.filter(id__in=ingred_dict.keys())
    shopping_list = [
        f'{ingred.name.capitalize()} ({ingred.measurement_unit}) - '
        f'{ingred_dict[ingred.id]}' for ingred in ingredients
    ]
    return shopping_list


def download_txt(shopping_list):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="Список покупок.txt"')
    response.write("Список покупок:\n\n")
    count = 0
    for ingredient_string in shopping_list:
        count += 1
        response.write(f"{count}. {ingredient_string}\n")
    return response
