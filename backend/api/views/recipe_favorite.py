from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from api.models import (
    Recipe,
    RecipeFavorite
)
from api.serializers import RecipeFavoriteSerializer
from core.utils import object_update_or_delete


class RecipeFavoriteMixin:
    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def change_favorite(self, request, pk):
        data = {
            'author': request.user,
            'recipe': get_object_or_404(Recipe, id=pk)
        }
        return object_update_or_delete(
            data=data,
            error_mesage='У вас нет данного рецепта в избранном.',
            model=RecipeFavorite,
            request=request,
            serializer_class=RecipeFavoriteSerializer
        )
