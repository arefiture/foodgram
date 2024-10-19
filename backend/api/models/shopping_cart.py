from django.contrib.auth import get_user_model
from django.db import models

from api.models.abstract_models import CookbookModel
from api.models.fields import UserForeignKey
from api.models.recipe import Recipe


User = get_user_model()


class ShoppingCart(CookbookModel):
    author = UserForeignKey(verbose_name='Владелец корзины покупок')
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta(CookbookModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_cart'
            )
        ]
        default_related_name = 'shopping_cart'
        verbose_name = 'Ингредиент с рецепта для покупок'
        verbose_name_plural = 'Ингредиенты с рецепта для покупок'
