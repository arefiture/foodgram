from re import sub as re_sub
from uuid import uuid4

from core.constants import MAX_LENGTH_SHORT_LINK


def generate_short_link() -> str:
    """Генерирует обрезанный до N знаков UUID4."""

    return uuid4().hex[:MAX_LENGTH_SHORT_LINK]


def to_snake_case(text: str) -> str:
    """Преобразовывает CamelCase в snake_case.

    Добавляет нижнее подчеркивание перед заглавными буквами, кроме первой
    буквы строки. После этого превращает все буквы в строчные и
    возвращает строку.
    """

    return re_sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
