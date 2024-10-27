from core.constants import COOKBOOK
from core.models import PrefixedDBModel


class CookbookBaseModel(PrefixedDBModel):
    prefix_name = COOKBOOK

    class Meta(PrefixedDBModel.Meta):
        abstract = True
