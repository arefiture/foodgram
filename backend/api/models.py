from django.db import models


class Tag(models.Model):
    # TODO: Написать manager и management-загрузку

    name = models.CharField(
        verbose_name='Наименование тега', max_length=32, unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг', max_length=32, unique=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'cookbook_tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    # TODO: Написать manager и management-загрузку

    name = models.CharField(
        verbose_name='Наименование ингредиента', max_length=32, unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерений', max_length=16
    )
    # TODO: Возможно, стоит единицы измерений вынести в отдельную модель

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'cookbook_ingredient'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
