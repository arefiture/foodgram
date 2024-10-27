from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from api.models.abstract_models import CookbookBaseModel
from api.models.fields import UserForeignKey
from api.models.ingredient import Ingredient
from api.models.tag import Tag
from core.constants import (
    LENGTH_CHARFIELD_256,
    MAX_LENGTH_SHORT_LINK,
    MIN_COOKING_TIME_ERROR,
    RECIPE_COOKING_TIME_MIN,
    RECIPE_DETAIL_URL,
    RECIPE_IMAGE_PATH,
)
from core.utils import generate_short_link

User = get_user_model()


class Recipe(CookbookBaseModel):

    tags = models.ManyToManyField(
        Tag, through='RecipeTags'
    )
    author = UserForeignKey(verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients'
    )
    name = models.CharField(
        verbose_name='Наименование рецепта',
        max_length=LENGTH_CHARFIELD_256
    )
    image = models.ImageField(
        verbose_name='Путь до картинки', blank=True,
        upload_to=RECIPE_IMAGE_PATH
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                RECIPE_COOKING_TIME_MIN,
                message=MIN_COOKING_TIME_ERROR),
        ]
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка', default=generate_short_link,
        max_length=MAX_LENGTH_SHORT_LINK
    )

    class Meta(CookbookBaseModel.Meta):
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return RECIPE_DETAIL_URL.format(pk=self.pk)
