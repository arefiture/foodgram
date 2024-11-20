from typing import Optional

from rest_framework.exceptions import ValidationError


class SubscribeUniqueValidator:
    """
    Валидатор для сравнения подписчика и автора.

    В случае если они равны вызывает исключение, т.к.
    подпись на самого себя не имеет смысла.
    """

    message = 'Невозможно подписаться на самого себя'

    def __init__(self, fields: list, message: Optional[str] = None):
        self.fields = fields
        self.message = message or self.message

    def __call__(self, attrs: dict):
        user = attrs.get('user')
        author_recipe = attrs.get('author_recipe')

        if user == author_recipe:
            raise ValidationError(self.message)


class UniqueDataInManyFieldValidator:
    """Валидатор на уникальность сложных полей."""

    def __init__(
        self, *, field: str, message: str,
        is_dict: bool = False, key: Optional[str] = None
    ):
        self.field = field
        self.message = message
        self.is_dict = is_dict
        if is_dict:
            if not key:
                raise ValueError(
                    {'message': 'Требуется передать поле key для поиска'}
                )
            self.search_field = key

    def __call__(self, value):
        data_list = value.get(self.field)
        data_set = {
            field.get(self.search_field) if self.is_dict else field
            for field in data_list
        }
        if len(data_list) != len(data_set):
            raise ValidationError(self.message)
