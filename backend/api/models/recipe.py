from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from api.models.base_models import CookbookBaseModel
from api.models.fields import UserForeignKey
from api.models.ingredient import Ingredient
from api.models.tag import Tag
from core.constants import (
    FRONTEND_DETAIL_URL,
    LENGTH_CHARFIELD_256,
    MAX_LENGTH_SHORT_LINK,
    MIN_COOKING_TIME_ERROR,
    RECIPE_COOKING_TIME_MIN,
    RECIPE_IMAGE_PATH
)
from core.utils import generate_short_link

User = get_user_model()


class Recipe(CookbookBaseModel):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        Tag, through='RecipeTags', verbose_name='Теги'
    )
    author = UserForeignKey(verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients', verbose_name='Ингредиенты'
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
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=now, editable=False
    )

    class Meta(CookbookBaseModel.Meta):
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return f'[{self.id}] {self.name}'

    def get_frontend_absolute_url(self) -> str:
        return FRONTEND_DETAIL_URL.format(pk=self.pk)
