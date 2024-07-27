from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import (RecipeIngredient)


def get_ingredients_from_shopping_list(user):
    ingredients = (
        RecipeIngredient.objects
        .filter(recipe__shopping_cart__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_amount=Sum('amount'))
        .order_by('ingredient__name')
    )
    shopping_list = [
        f"{item['ingredient__name'].capitalize()} "
        f"({item['ingredient__measurement_unit']}) - {item['total_amount']}"
        for item in ingredients
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
