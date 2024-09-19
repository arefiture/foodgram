from rest_framework import serializers

from api.models import Ingredient, Recipe, Tag
from core.serializers import Base64ImageField
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)

    def to_internal_value(self, data):
        if isinstance(data, int):
            return data
        else:
            raise serializers.ValidationError("Для тега ожидается число.")


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True, read_only=True
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'name', 'image', 'text', 'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'name', 'image', 'text', 'cooking_time',
        )

    def create(self, validated_data):
        current_user = self.context['request'].user
        validated_data['author'] = current_user
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return recipe
