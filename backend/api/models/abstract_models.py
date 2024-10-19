from django.db import models

from core.constants import COOKBOOK
from core.utils import to_snake_case


class CookbookModel(models.Model):
    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        table_name = to_snake_case(cls.__name__)
        cls.Meta.db_table = f'{COOKBOOK}_{table_name}'
