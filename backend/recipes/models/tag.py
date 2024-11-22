from django.db import models

from core.constants import LENGTH_CHARFIELD_32
from recipes.models.base_models import CookbookBaseModel


class Tag(CookbookBaseModel):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Наименование тега',
        max_length=LENGTH_CHARFIELD_32,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=LENGTH_CHARFIELD_32,
        unique=True
    )

    class Meta(CookbookBaseModel.Meta):
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name.capitalize()
