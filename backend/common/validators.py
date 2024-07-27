from rest_framework.serializers import ValidationError


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
