from django.db import models

from recipes.models.base_models import CookbookBaseModel
from recipes.models.recipe import Recipe
from recipes.models.tag import Tag


class RecipeTags(CookbookBaseModel):
    """Модель связи рецептов и тегов."""

    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        to=Tag, verbose_name='Тег', on_delete=models.CASCADE
    )

    class Meta(CookbookBaseModel.Meta):
        default_related_name = 'recipe_tags'
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'Рецепт #{self.recipe.id} - Тег #{self.tag.id}'
