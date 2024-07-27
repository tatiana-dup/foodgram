import re

from django.core.exceptions import ValidationError


def validate_username(value):
    pattern = r'^[\w.@+-]+\Z'

    if not re.match(pattern, value):
        invalid_chars = re.sub(pattern, '', value)
        raise ValidationError(
            'Введите корректный юзернейм. '
            f'Эти символы недопустимы: {invalid_chars}'
        )
