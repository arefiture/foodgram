from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.validators import (
    UniqueTogetherValidator
)

from api.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    RecipeFavorite,
    ShoppingCart,
    Tag
)
from core.constants import (
    REPEAT_ADDED_FAVORITE_ERROR,
    REPEAT_ADDED_SHOPPING_CART_ERROR
)
from core.serializers import (
    BaseRecipeSerializer
)
from core.utils import many_unique_with_minimum_one_validate
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


class AbstractRecipeSerializer(BaseRecipeSerializer):
    """Абстрактный сериалайзер рецептов.

    Содержит дополнительные поля для базового сериалайзера рецептов:
    теги, ингредиенты, автор и описание.
    """
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientsGetSerializer(
        many=True,
        source='recipe_ingredients',
    )

    class Meta(BaseRecipeSerializer.Meta):
        abstract = True
        fields = (
            *BaseRecipeSerializer.Meta.fields,
            'tags', 'ingredients', 'author', 'text'
        )


class RecipeGetSerializer(AbstractRecipeSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(AbstractRecipeSerializer.Meta):
        fields = (
            *AbstractRecipeSerializer.Meta.fields,
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = fields

    def get_is_exists(self, obj, model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(
            author=request.user, recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        return self.get_is_exists(obj, RecipeFavorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_exists(obj, ShoppingCart)


class RecipeChangeSerializer(AbstractRecipeSerializer):
    """Сериалайзер для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        required=True
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientsSetSerializer(
        many=True,
        source='recipe_ingredients',
    )

    class Meta(AbstractRecipeSerializer.Meta):
        read_only_fields = ('author', )

    """
    Сообщение ревьюверу:
    Я пробовал делать через validate_<field>, но столкнулся с проблемой -
    мне приходилось делать дополнительные проверки внутри update-метода.
    https://gist.github.com/arefiture/bb78eac18e495ab6b8cec3db41c7d771
    Мне такой подход не понравился
    """
    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        many_unique_with_minimum_one_validate(
            data_list=ingredients, field_name='ingredients',
            singular='ингредиент', plural='ингредиенты'
        )

        tags = data.get('tags')
        many_unique_with_minimum_one_validate(
            data_list=tags, field_name='tags',
            singular='тег', plural='теги'
        )

        return data

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
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.added_tags_ingredients(
            ingredients=ingredients, recipe=recipe, tags=tags
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self.added_tags_ingredients(
            ingredients=ingredients, recipe=instance, tags=tags
        )
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context=self.context
        ).data


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
        error_message = REPEAT_ADDED_SHOPPING_CART_ERROR


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('ingredients',)

    def get_ingredients(self, obj):
        author = self.context.get('request').user
        # TODO: фильтр ниже вынести в менеджен
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
        error_message = REPEAT_ADDED_FAVORITE_ERROR
