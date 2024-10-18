from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from api.models import Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        author = self.request.user
        if not value or not author.is_authenticated:
            return queryset
        if value:
            return queryset.filter(recipe_favorite__author=author)
        return queryset.exclude(recipe_favorite__author=author)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        author = self.request.user
        if not author.is_authenticated:
            return queryset
        if value:
            return queryset.filter(shopping_cart__author=author)
        return queryset.exclude(shopping_cart__author=author)
