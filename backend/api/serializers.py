from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    RecipeFavorite,
    ShoppingCart,
    Tag
)
from core.serializers import Base64ImageField
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientsSetSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
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

    def validate(self, attrs):
        # TODO: подумать об общем валидаторе и избавлении от повторов
        ingredients = attrs.get('recipe_ingredients')
        tags = attrs.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходим хотя бы один ингредиент.'
            )
        if not tags:
            raise serializers.ValidationError(
                'Необходим хотя бы один тег.'
            )

        set_ingredients = set(
            ingredient.get('id') for ingredient in ingredients
        )
        set_tags = set(tags)
        if len(ingredients) != len(set_ingredients):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        if len(tags) != len(set_tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredients.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        # TODO: Возможно, нужно списки ингров и теги очищать и брать из запроса
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        existing_ingredients = set(
            RecipeIngredients.objects.values_list('ingredient', flat=True)
        )
        for ingredient in ingredients:
            base_ingredient = ingredient.get('id')
            if base_ingredient in existing_ingredients:
                raise serializers.ValidationError(
                    {'errors': 'нельзя добавить два одинаковых ингредиента'}
                )
            _, created = RecipeIngredients.objects.update_or_create(
                recipe=instance, ingredient=base_ingredient,
                defaults={'amount': ingredient.get('amount')}
            )
        instance.save()
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
