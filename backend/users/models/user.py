from django.db import models
from django.contrib.auth.models import AbstractUser

from core.constants import (
    LENGTH_CHARFIELD_150,
    USER_AVATAR_PATH,
    USER_EMAIL_ERROR,
    USER_USERNAME_ERROR
)
from users.models.abstract_models import AuthBaseModel


class User(AuthBaseModel, AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': USER_EMAIL_ERROR,
        },
    )

    username = models.CharField(
        verbose_name='Никнейм пользователя',
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': USER_USERNAME_ERROR,
        },
        max_length=LENGTH_CHARFIELD_150
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LENGTH_CHARFIELD_150
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGTH_CHARFIELD_150
    )

    avatar = models.ImageField(
        verbose_name='Аватар',
        blank=True,
        upload_to=USER_AVATAR_PATH
    )

    subscribers = models.ManyToManyField(
        'self', related_name='subscribed_users', through='Subscription'
    )

    class Meta(AuthBaseModel.Meta):
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username
