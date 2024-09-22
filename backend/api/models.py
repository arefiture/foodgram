from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.utils import generate_short_link

User = get_user_model()


class Tag(models.Model):
    # TODO: Написать manager и management-загрузку

    name = models.CharField(
        verbose_name='Наименование тега', max_length=32, unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг', max_length=32, unique=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'cookbook_tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class Ingredient(models.Model):
    # TODO: Написать manager и management-загрузку

    name = models.CharField(
        verbose_name='Наименование ингредиента', max_length=128, unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерений', max_length=64
    )
    # TODO: Возможно, стоит единицы измерений вынести в отдельную модель

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'cookbook_ingredient'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag, through='RecipeTags'
    )
    author = models.ForeignKey(
        to=User, verbose_name='Автор рецепта', on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients'
    )
    name = models.CharField(
        verbose_name='Наименование рецепта', max_length=256
    )
    image = models.ImageField(
        verbose_name='Путь до картинки', blank=True, upload_to='recipe/'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1,
                message='Время не может быть меньше 1 минуты'),
        ]
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка', default=generate_short_link,
        max_length=6
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'cookbook_recipe'
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        to=Tag, verbose_name='Тег', on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'cookbook_recipe_tags'
        default_related_name = 'recipe_tags'
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество в рецепте',
        validators=[
            MinValueValidator(
                1,
                message='Количество должно быть равно 1 или больше.'),
        ]
    )

    class Meta:
        db_table = 'cookbook_recipe_ingredients'
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
