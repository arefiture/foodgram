from core.constants import COOKBOOK
from core.models import PrefixedDBModel


class CookbookBaseModel(PrefixedDBModel):
    """
    Заготовка для моделей, связанных с рецептами.

    С помощью PrefixedDBModel.__init_subclass__ назначает
    новый префикс для таблиц (вместо api значение из COOKBOOK).
    """

    prefix_name = COOKBOOK

    class Meta(PrefixedDBModel.Meta):
        abstract = True
