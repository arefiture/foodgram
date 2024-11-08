from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from api.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ['name']


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

    def filter_or_exclude_author(
        self, queryset, name, value, filter_field
    ):
        author = self.request.user
        if value and author.is_authenticated:
            return queryset.filter(**{filter_field: author})
        elif not value and author.is_authenticated:
            return queryset.exclude(**{filter_field: author})
        elif not value and author.is_anonymous:
            return queryset.all()
        return queryset.none()

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_or_exclude_author(
            queryset, name, value, filter_field='recipe_favorite__author'
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_or_exclude_author(
            queryset, name, value, filter_field='shopping_cart__author'
        )
