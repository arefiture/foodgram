from uuid import uuid4

from django.db import models
from rest_framework import serializers, status, request, response


def generate_short_link():
    return uuid4().hex[:6]


def object_update_or_delete(
    *,
    data: dict[str: object],
    error_mesage: str,
    model: models.Model,
    request: request.Request,
    serializer_class: serializers.Serializer
) -> response.Response:
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )
    instance = model.objects.filter(**data)
    if not instance.exists():
        return response.Response(
            {'errors': error_mesage},
            status=status.HTTP_400_BAD_REQUEST
        )
    instance.delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)
