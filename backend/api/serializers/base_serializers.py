"""
Для ревьювера: Я знаю, что у <ClassSerializer>.Meta нет
атрибута abstract. Само слово abstract в данном случае
несёт поясняющий характер, не более.
"""

import base64

from django.core.files.base import ContentFile
from recipes.models.abstract_models import BaseActionRecipeModel
from recipes.models.recipe import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.serializers.user import UserSerializer


class Base64ImageField(serializers.ImageField):
    """Сериалайзер под картинки. Преобразует входные данные в Base64."""

    def to_internal_value(self, data: str):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.Serializer):
    """Сериалайзер под аватар."""

    avatar = Base64ImageField(required=False)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """
    Базовый сериалайзер рецептов.

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


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления рецептов и авторов в связанные таблицы.

    Используется при добавлении в корзину, в избранные.
    """

    author = UserSerializer
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = None  # Назначаем у дочерних классов
        fields = ('author', 'recipe')
        error_message = ''

    @classmethod
    def get_validators(cls):
        return [
            UniqueTogetherValidator(
                queryset=cls.Meta.model.objects.all(),
                fields=('author', 'recipe'),
                message=cls.Meta.error_message
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.validators = self.get_validators()

    def to_representation(self, instance: BaseActionRecipeModel):
        return BaseRecipeSerializer(instance.recipe).data
