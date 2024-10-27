from rest_framework import serializers

from api.models import RecipeIngredients, ShoppingCart
from api.serializers.abstract import BaseRecipeActionSerializer
from core.constants import REPEAT_ADDED_SHOPPING_CART_ERROR


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
        return RecipeIngredients.shopping_list.get_queryset(author)
