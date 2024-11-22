from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.abstract_models import BaseActionRecipeModel

User = get_user_model()


class ShoppingCart(BaseActionRecipeModel):
    """Модель корзины покупок."""

    class Meta(BaseActionRecipeModel.Meta):
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
