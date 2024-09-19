from django.db import models


class Tag(models.Model):
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
