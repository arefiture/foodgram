import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from api.models import Recipe


class Base64ImageField(serializers.ImageField):
    """Сериалайзер под картинки. Преобразует входные данные в Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


# Мне не нравится этот сериалайзер в данном файле.
# Возможно ли как-то его поместить в api.serializers.
# И избежать связи serializer'ов api → users, users → api.
class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер рецептов.

    Содержит минимум необходимых полей для ответов на некоторые запросы.
    В перечень полей входят:
    - id
    - name
    - image
    - cooking_time
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
