from collections import OrderedDict
from re import sub as re_sub
from uuid import uuid4

from django.db.models import Model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ValidationError

from core.constants import (
    MAX_LENGTH_SHORT_LINK,
    TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR,
    TEMPLATE_MESSAGE_UNIQUE_ERROR
)


def generate_short_link() -> str:
    """Генерирует обрезанный до N знаков UUID4."""

    return uuid4().hex[:MAX_LENGTH_SHORT_LINK]


def object_update(*, serializer: Serializer) -> Response:
    """
    Функция для обновления данных из action.

    Принимает в себя:
    * serializer - готовый объект сериалайзера.
    """

    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data, status=status.HTTP_201_CREATED
    )


def object_delete(
    *,
    data: dict[str: object],
    error_mesage: str,
    model: Model
) -> Response:
    """
    Функция для удаления данных из action.

    Принимает в себя:
    * data - словарь данных для проверки в модели. Из данного словаря
    также берутся данные по id для создания сериалайзера
    * error_mesage - текст ошибки при удалении, если удаляемый элемент
    отсутствует в БД
    * model - модель данных
    """

    instance = model.objects.filter(**data)
    if not instance.exists():
        return Response(
            {'errors': error_mesage},
            status=status.HTTP_400_BAD_REQUEST
        )
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# TODO: удалить
def object_update_or_delete(
    *,
    data: dict[str: object],
    error_mesage: str,
    model: Model,
    request: Request,
    serializer_class: Serializer
) -> Response:
    """
    Функция для обновления и удаления данных из action.

    Принимает в себя:
    * data - словарь данных для проверки в модели. Из данного словаря
    также берутся данные по id для создания сериалайзера
    * error_mesage - текст ошибки при удалении, если удаляемый элемент
    отсутствует в БД
    * model - модель данных
    * request - данные запроса
    * serializer_class - класс сериализатора
    """

    serializer = serializer_class(
        # Возможно, тут стоит добавить проверку на наличие id...
        data={key: obj.id for key, obj in data.items()},
        context={'request': request}
    )
    if request.method == 'POST':
        return object_update(serializer=serializer)
    return object_delete(data=data, error_mesage=error_mesage, model=model)


def many_unique_with_minimum_one_validate(
    data_list: list, field_name: str, singular: str, plural: str
) -> None:
    """
    Валидация many-полей на их наличие и уникальность.

    Функция может работать как с [model.objects], так и с [OrderedDict()].
    * data_list - валидируемые данные (список, т.к. many=True)
    * field_name - наименование поля валидации для его указания в ошибке
    * singular - наименование в единственном числе на русском
    * plural - наименование во множественном числе на русском
    """

    if not data_list:
        raise ValidationError({
            field_name: TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR.format(
                field_name=singular.lower()
            )
        })

    if isinstance(data_list[0], OrderedDict):
        data_set = {data.get('id') for data in data_list}
    else:
        data_set = {data.id for data in data_list}

    if len(data_list) != len(data_set):
        raise ValidationError({
            field_name: TEMPLATE_MESSAGE_UNIQUE_ERROR.format(
                field_name=plural.capitalize()
            )
        })


def to_snake_case(text: str) -> str:
    """Преобразовывает CamelCase в snake_case.

    Добавляет нижнее подчеркивание перед заглавными буквами, кроме первой
    буквы строки. После этого превращает все буквы в строчные и
    возвращает строку.
    """

    return re_sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
