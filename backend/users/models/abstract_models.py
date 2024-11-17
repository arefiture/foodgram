from core.constants import AUTH
from core.models import PrefixedDBModel


class AuthBaseModel(PrefixedDBModel):
    """
    Заготовка для моделей, связанных с пользователями.

    С помощью PrefixedDBModel.__init_subclass__ назначает
    новый префикс для таблиц (вместо users значение из AUTH).
    """

    prefix_name = AUTH

    class Meta(PrefixedDBModel.Meta):
        abstract = True
