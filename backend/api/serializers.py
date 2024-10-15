from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.validators import (
    UniqueTogetherValidator
)

from api.decorators import unique_with_minimum_one
from api.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    RecipeFavorite,
    ShoppingCart,
    Tag
)
from core.constants import (
    TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR,
)
from core.serializers import (
    Base64ImageField,
    BaseRecipeSerializer
)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер по теги."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер по ингредиенты."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientsSetSerializer(serializers.ModelSerializer):
    """Сериалайзер связующей рецепты+ингредиенты на запись."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsGetSerializer(serializers.ModelSerializer):
    """Сериалайзер связующей рецепты+ингредиенты на чтение."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания рецептов."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        required=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSetSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image', 'is_favorited',
            'is_in_shopping_cart', 'name', 'text', 'cooking_time'
        )

    @unique_with_minimum_one(
        singular='тег', plural='Теги'
    )
    def validate_tags(self, value_list):
        value_set = {field for field in value_list}
        return value_set

    @unique_with_minimum_one(
        singular='ингредиент', plural='Ингредиенты'
    )
    def validate_ingredients(self, value_list):
        value_set = {field.get('id') for field in value_list}
        return value_set

    def added_tags_ingredients(self, *, ingredients, recipe, tags):
        recipe.tags.set(tags)
        ingredient_recipe = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredient_recipe)

    def create(self, validated_data: dict):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.added_tags_ingredients(
            ingredients=ingredients, recipe=recipe, tags=tags
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients', None)
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR.format(
                    field_name='ингредиент'
                )
            })
        tags = validated_data.pop('tags', None)
        if not tags:
            raise serializers.ValidationError({
                'tags': TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR.format(
                    field_name='тег'
                )
            })
        super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self.added_tags_ingredients(
            ingredients=ingredients, recipe=instance, tags=tags
        )
        return instance

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        recipe['ingredients'] = RecipeIngredientsGetSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data
        return recipe

    def get_is_favorited(self, obj):
        return True

    def get_is_in_shopping_cart(self, obj):
        return True


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    author = UserSerializer
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        abstract = True
        model = None
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

    def to_representation(self, instance):
        return BaseRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    class Meta(BaseRecipeActionSerializer.Meta):
        model = ShoppingCart
        error_message = 'Нельзя повторно добавить рецепт в корзину'


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('ingredients',)

    def get_ingredients(self, obj):
        author = self.context.get('request').user
        ingredients = RecipeIngredients.objects.filter(
            recipe__shopping_cart__author=author
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')
        return ingredients


class RecipeFavoriteSerializer(BaseRecipeActionSerializer):
    class Meta(BaseRecipeActionSerializer.Meta):
        model = RecipeFavorite
        error_message = 'Нельзя повторно добавить рецепт в избранные'
