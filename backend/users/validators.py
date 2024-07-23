import re
from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == "me":
        raise ValidationError(
            "Вы не можете выбрать юзернейм 'me', "
            "выберите другой юзернейм.")

    pattern = r'^[\w.@+-]+\Z'

    if not re.match(pattern, value):
        invalid_chars = re.sub(pattern, '', value)
        raise ValidationError(
            f'Введите корректный юзернейм. '
            f'Эти символы недопустимы: {invalid_chars}'
        )
