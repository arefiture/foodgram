from django.contrib.auth import get_user_model
from django.db import models

from api.models.abstract_models import CookbookModel
from api.models.fields import UserForeignKey
from api.models.recipe import Recipe


User = get_user_model()


class RecipeFavorite(CookbookModel):
    author = UserForeignKey(verbose_name='Владелец корзины покупок')
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_recipe_favorite'
            )
        ]
        default_related_name = 'recipe_favorite'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
