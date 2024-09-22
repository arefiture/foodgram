from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from api.models import Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    # is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    # is_in_shopping_cart = filters.BooleanFilter(
    #     method='filter_is_in_shopping_cart'
    # )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    # def filter_is_favorited(self, queryset, name, value):
    #     return queryset

    # def filter_is_in_shopping_cart(self, queryset, name, value):
    #     return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
