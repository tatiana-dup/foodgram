from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError('Время не может быть меньше 1 минуты')
    if value > 1440:
        raise ValidationError(
            'Текущее время превышает сутки. Укажите меньшее значение')
