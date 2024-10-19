from django.db import models

from api.models.abstract_models import CookbookModel
from api.models.recipe import Recipe
from api.models.tag import Tag


class RecipeTags(CookbookModel):
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        to=Tag, verbose_name='Тег', on_delete=models.CASCADE
    )

    class Meta:
        default_related_name = 'recipe_tags'
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
