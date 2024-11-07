import csv
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from api.models import Recipe, ShoppingCart
from api.serializers import (
    DownloadShoppingCartSerializer,
    ShoppingCartSerializer
)
from core.utils import object_update_or_delete


class ShoppingCartMixin:
    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def change_shopping_cart(self, request, pk):
        data = {
            'author': request.user,
            'recipe': get_object_or_404(Recipe, id=pk)
        }
        return object_update_or_delete(
            data=data,
            error_mesage='У вас нет данного рецепта в корзине.',
            model=ShoppingCart,
            request=request,
            serializer_class=ShoppingCartSerializer
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        serializer = DownloadShoppingCartSerializer(
            instance=ShoppingCart.objects.all(),
            many=True, context={'request': request}
        )

        now = datetime.now()
        formatted_time = now.strftime('%d-%m-%Y_%H_%M_%S')

        response = HttpResponse(content_type='text/csv')
        filename = f'shopping_cart.csv_{request.user.id}_{formatted_time}'
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )

        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
        if serializer.data:
            ingredients = serializer.data[0]['ingredients']

            rows = map(
                lambda ingredient: [
                    ingredient['name'],
                    ingredient['measurement_unit'],
                    ingredient['total_amount']
                ], ingredients
            )
            writer.writerows(rows)

        return response
