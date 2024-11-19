from django.contrib.auth import get_user_model
from django.db import models

from api.models.base_models import CookbookBaseModel
from api.models.fields import UserForeignKey
from api.models.recipe import Recipe

User = get_user_model()


class BaseActionRecipeModel(CookbookBaseModel):
    """
    Заготовка для моделей, связанных с добавление рецептов куда-либо.

    Примеры: добавление рецепта в избранное, в корзину.
    """

    author = UserForeignKey(verbose_name='Владелец корзины покупок')
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta(CookbookBaseModel.Meta):
        abstract = True
        # Хотел сюда еще ограничение уникальности вынести, определяя имя
        # через cls.__name__, но что бы я не делал - в миграции не попадают.
        # Походу, это не реально для текущей версии:
        # https://stackoverflow.com/questions/57149015/creating-a-models-uniqueconstraint-in-abstract-model
