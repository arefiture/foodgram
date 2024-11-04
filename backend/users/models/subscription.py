from django.db import models

from users.models.abstract_models import AuthBaseModel
from users.models.user import User


class Subscription(AuthBaseModel):
    author_recipe = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors',
        verbose_name='Автор рецепта'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users',
        verbose_name='Подписчик'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(AuthBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author_recipe', 'user'),
                name='unique_author_recipe_user'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.author_recipe.__str__()} -> {self.user.__str__()}'
