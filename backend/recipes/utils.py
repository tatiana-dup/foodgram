import random
import string

from django.http import HttpResponse

from recipes.models import (Ingredient,
                            RecipeIngredient,
                            RecipeShortLink,
                            ShoppingCart)


def generate_unique_short_code():
    while True:
        short_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=3))
        if not RecipeShortLink.objects.filter(short_code=short_code).exists():
            return short_code


def get_ingredients_from_shopping_list(user):
    recipe_ids = user.shoppingcart_set.values_list('recipe_id', flat=True)
    ingredients_list = RecipeIngredient.objects.filter(recipe_id__in=recipe_ids).values('ingredient_id', 'amount')
    ingred_dict = {}
    for item in ingredients_list:
        ingred_id = item['ingredient_id']
        amount = item['amount']
        if ingred_id in ingred_dict:
            amount = amount + ingred_dict[ingred_id]
        ingred_dict[ingred_id] = amount
    ingredients = Ingredient.objects.filter(id__in=ingred_dict.keys())
    shopping_list = [
        f'{ingred.name.capitalize()} ({ingred.measurement_unit}) - {ingred_dict[ingred.id]}'
        for ingred in ingredients
    ]
    # print(shopping_list)
    return shopping_list


def download_txt(shopping_list):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="Список покупок.txt"'
    response.write("Список покупок:\n\n")
    for ingredient_string in shopping_list:
        response.write(f"{ingredient_string}\n")
    return response
