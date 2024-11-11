from django.db import models

from api.models.abstract_models import CookbookBaseModel
from core.constants import LENGTH_CHARFIELD_64, LENGTH_CHARFIELD_128


class Ingredient(CookbookBaseModel):
    # TODO: Написать manager и management-загрузку

    name = models.CharField(
        verbose_name='Наименование ингредиента',
        max_length=LENGTH_CHARFIELD_128,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерений',
        max_length=LENGTH_CHARFIELD_64
    )
    # TODO: Возможно, стоит единицы измерений вынести в отдельную модель

    class Meta(CookbookBaseModel.Meta):
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name.capitalize()} - {self.measurement_unit}.'
