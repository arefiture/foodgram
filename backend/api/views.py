import csv
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.models import (
    Ingredient,
    Recipe,
    RecipeFavorite,
    ShoppingCart,
    Tag
)
from api.serializers import (
    DownloadShoppingCartSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeFavoriteSerializer,
    ShoppingCartSerializer,
    TagSerializer
)
from users.permissions import (
    IsAuthor,
    ReadOnly
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [ReadOnly]
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.request.method in ("GET", "POST"):
            self.permission_classes = [IsAuthenticated | ReadOnly]
        elif self.request.method in ("PATCH", "DELETE"):
            self.permission_classes = [IsAuthor]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        # if self.request.method in SAFE_METHODS:
        #     return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk):
        try:
            recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {'message': 'Не существует такой записи'},
                status=status.HTTP_404_NOT_FOUND
            )

        scheme = request.scheme
        host = request.get_host()
        domain = f'{scheme}://{host}'
        return Response(
            {'short-link': f'{domain}/s/{recipe.short_link}'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def change_shopping_cart(self, request, pk):
        author = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data={'author': author.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart = ShoppingCart.objects.filter(
            author=author, recipe=recipe
        )
        if not shopping_cart.exists():
            return response.Response(
                {'errors': 'У вас нет данного рецепта в корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

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

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def change_favorite(self, request, pk):
        author = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeFavoriteSerializer(
            data={'author': author.id, 'recipe': recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        favorite = RecipeFavorite.objects.filter(
            author=author, recipe=recipe
        )
        if not favorite.exists():
            return response.Response(
                {'errors': 'У вас нет данного рецепта в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
