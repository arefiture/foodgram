from recipes.models import RecipeFavorite

from api.serializers.base_serializers import BaseRecipeActionSerializer
from core.constants import REPEAT_ADDED_FAVORITE_ERROR


class RecipeFavoriteSerializer(BaseRecipeActionSerializer):
    """Сериалайзер избранных рецептов."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = RecipeFavorite
        error_message = REPEAT_ADDED_FAVORITE_ERROR
