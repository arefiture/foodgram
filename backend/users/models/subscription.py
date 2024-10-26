from django.db import models

from users.models.abstract_models import AuthBaseModel
from users.models.user import User


class Subscription(AuthBaseModel, models.Model):
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followings',
        verbose_name='Автор рецепта'
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Подписчик'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(AuthBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('followed', 'follower'),
                name='unique_followed_foolower'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.followed.__str__()} -> {self.follower.__str__()}'
