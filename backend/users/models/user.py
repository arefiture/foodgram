from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone

from core.constants import (
    LENGTH_CHARFIELD_128,
    LENGTH_CHARFIELD_150,
    SUPERUSER_STAFF_ERROR,
    USER_AVATAR_PATH,
    USER_EMAIL_ERROR,
    USER_USERNAME_ERROR
)
from users.models.abstract_models import AuthBaseModel


class UserManager(BaseUserManager):

    def create_user(
        self, email, username, first_name, last_name,
        password=None, **extra_fields
    ):
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name,
            last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, username, first_name, last_name,
        password=None, **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(SUPERUSER_STAFF_ERROR)

        return self.create_user(
            email, username, first_name, last_name,
            password, **extra_fields
        )


class User(AuthBaseModel, AbstractBaseUser):

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
    password = models.CharField(
        verbose_name='Пароль',
        max_length=LENGTH_CHARFIELD_128
    )
    username = models.CharField(
        verbose_name='Никнейм пользователя',
        unique=True,
        validators=[UnicodeUsernameValidator()],
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
    is_staff = models.BooleanField(
        verbose_name='Статус админа',
        default=False,
        help_text=(
            'Определяет, может ли пользователь войти на '
            'страницу администратора.'
        ),
    )
    is_active = models.BooleanField(
        verbose_name='Активность учетной записи',
        default=True,
        help_text=(
            'Определяет, следует ли считать пользователя активным. '
            'Уберите флажок вместо удаления учетной записи.'
        ),
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        default=timezone.now
    )
    last_login = models.DateTimeField(
        verbose_name='Последний вход',
        blank=True,
        null=True
    )
    subscribers = models.ManyToManyField(
        'self', related_name='subscribed_users', through='Subscription'
    )

    objects = UserManager()

    class Meta(AuthBaseModel.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['date_joined']

    def __str__(self) -> str:
        return self.username

    def clean(self):
        """Валидация объекта перед сохранением в БД."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        """Возвращает имя и фамилию через разделить (пробел)."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self) -> str:
        """Возвращает только имя пользователя."""
        return self.first_name
