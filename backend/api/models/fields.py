from django.contrib.auth import get_user_model
from django.db.models import CASCADE, ForeignKey

User = get_user_model()


class UserForeignKey(ForeignKey):
    """
    FK-поле для пользователей.

    По-умолчанию:
    - to=User (модель берётся из get_user_model)
    - on_delete=CASCADE
    """
    def __init__(self, verbose_name, **kwargs):
        return super().__init__(
            to=User,
            verbose_name=verbose_name,
            on_delete=CASCADE,
            *kwargs
        )
