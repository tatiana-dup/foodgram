import re
from django.core.exceptions import ValidationError


def validate_username(value):
    pattern = r'^[\w.@+-]+\Z'

    if not re.match(pattern, value):
        invalid_chars = re.sub(pattern, '', value)
        raise ValidationError(
            f'Введите корректный юзернейм. '
            f'Эти символы недопустимы: {invalid_chars}'
        )


def validate_recipes_limit(value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError(
            'Ограничение для количества рецептов '
            'должно быть целым числом.')
    if value < 0:
        raise ValidationError(
            'Ограничение для количества рецептов '
            'не может быть меньше нуля.')
    return value
