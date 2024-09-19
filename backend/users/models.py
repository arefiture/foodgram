from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

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
            'unique': 'Данный адрес уже используется.',
        },
    )

    username = models.CharField(
        verbose_name='Никнейм пользователя',
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': 'Пользователь с таким ником уже существует.',
        },
        max_length=150
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    avatar = models.ImageField(
        verbose_name='Аватар',
        blank=True,
        upload_to='users/'
    )

    subscribers = models.ManyToManyField(
        'self', related_name='subscribed_users', through='Subscription'
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followings'
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cookbook_subscription'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.followed.__str__()} -> {self.follower.__str__()}'
