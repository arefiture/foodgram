from django.contrib.auth import get_user_model
from django.db import models

from api.models.abstract_models import CookbookBaseModel
from api.models.fields import UserForeignKey
from api.models.recipe import Recipe


User = get_user_model()


class ShoppingCart(CookbookBaseModel):
    author = UserForeignKey(verbose_name='Владелец корзины покупок')
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta(CookbookBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_cart'
            )
        ]
        default_related_name = 'shopping_cart'
        verbose_name = 'рецепт к покупке'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self) -> str:
        return f'Рецепт #{self.recipe.id}'
