from core.constants import AUTH
from core.models import PrefixedDBModel


class AuthBaseModel(PrefixedDBModel):
    prefix_name = AUTH

    class Meta(PrefixedDBModel.Meta):
        abstract = True
