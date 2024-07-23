from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError('Время не может быть меньше 1 минуты')
    if value > 1440:
        raise ValidationError(
            'Текущее превышает превышает сутки. Укажите меньшее значение')


def validate_tag(value):
    if not Tag.objects.filter(pk=value):
        raise ValidationError('Такого тэга не существует')
