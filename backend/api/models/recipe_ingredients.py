from django.core.validators import MinValueValidator
from django.db import models

from api.models.abstract_models import CookbookModel
from api.models.ingredient import Ingredient
from api.models.recipe import Recipe
from core.constants import (
    MIN_INGREDIENT_AMOUNT_ERROR,
    INGREDIENT_AMOUNT_MIN
)


class RecipeIngredientsQuerySet(models.QuerySet):

    def get_sum_amount(self) -> "RecipeIngredientsQuerySet":
        return self.annotate(total_amount=models.Sum('amount'))

    def order_by_ingredient_name(self) -> "RecipeIngredientsQuerySet":
        return self.order_by('ingredient__name')

    def rename_fields(self) -> "RecipeIngredientsQuerySet":
        self.values(
            name=models.F('ingredient__name'),
            measurement_unit=models.F('ingredient__measurement_unit')
        )


class ShopCartListManager(models.Manager):

    def get_queryset(self, author) -> RecipeIngredientsQuerySet:
        return (
            RecipeIngredientsQuerySet(self.model)
            .filter(recipe__shopping_cart__author=author)
            .rename_fields()
            .get_sum_amount()
            .order_by_ingredient_name()
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

    objects = RecipeIngredientsQuerySet.as_manager()
    shopping_list = ShopCartListManager()

    class Meta(CookbookModel.Meta):
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
