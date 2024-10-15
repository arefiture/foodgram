from functools import wraps

from rest_framework.exceptions import ValidationError

from core.constants import (
    TEMPLATE_MESSAGE_UNIQUE_ERROR,
    TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR
)


def unique_with_minimum_one(singular: str, plural: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, value, *args, **kwargs):
            error_minimum_one = (
                TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR.format(
                    field_name=singular.lower()
                )
            )
            error_unique = (
                TEMPLATE_MESSAGE_UNIQUE_ERROR.format(
                    field_name=plural.capitalize()
                )
            )

            if not value:
                raise ValidationError(error_minimum_one)

            # Получаем список из функции, т.к. логика получения списка
            # зависит от типа данных в value
            set_value = func(self, value, *args, **kwargs)
            if len(set_value) != len(value):
                raise ValidationError(error_unique)

            return value
        return wrapper
    return decorator
