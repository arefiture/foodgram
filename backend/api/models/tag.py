from django.db import models

from api.models.abstract_models import CookbookBaseModel
from core.constants import LENGTH_CHARFIELD_32


class Tag(CookbookBaseModel):
    # TODO: Написать manager и management-загрузку

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
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
