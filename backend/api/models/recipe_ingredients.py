from django.core.validators import MinValueValidator
from django.db import models

from api.models.abstract_models import CookbookModel
from api.models.ingredient import Ingredient
from api.models.recipe import Recipe
from core.constants import (
    MIN_INGREDIENT_AMOUNT_ERROR,
    INGREDIENT_AMOUNT_MIN
)


class RecipeIngredients(CookbookModel):
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество в рецепте',
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN,
                message=MIN_INGREDIENT_AMOUNT_ERROR),
        ]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
