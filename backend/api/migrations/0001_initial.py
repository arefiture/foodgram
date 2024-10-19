# Generated by Django 3.2.3 on 2024-10-19 18:49

import api.models.fields
import core.utils
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Наименование ингредиента')),
                ('measurement_unit', models.CharField(max_length=64, verbose_name='Единицы измерений')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'db_table': 'cookbook_ingredient',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование рецепта')),
                ('image', models.ImageField(blank=True, upload_to='recipes/images/', verbose_name='Путь до картинки')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время не может быть меньше 1 минуты.')], verbose_name='Время приготовления (в минутах)')),
                ('short_link', models.CharField(default=core.utils.generate_short_link, max_length=6, verbose_name='Короткая ссылка')),
                ('author', api.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'db_table': 'cookbook_recipe',
                'ordering': ['name'],
                'abstract': False,
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='Наименование тега')),
                ('slug', models.SlugField(max_length=32, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'db_table': 'cookbook_tag',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', api.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Владелец корзины покупок')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='api.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Ингредиент с рецепта для покупок',
                'verbose_name_plural': 'Ингредиенты с рецепта для покупок',
                'db_table': 'cookbook_shopping_cart',
                'abstract': False,
                'default_related_name': 'shopping_cart',
            },
        ),
        migrations.CreateModel(
            name='RecipeTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tags', to='api.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tags', to='api.tag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Тег рецепта',
                'verbose_name_plural': 'Теги рецептов',
                'db_table': 'cookbook_recipe_tags',
                'abstract': False,
                'default_related_name': 'recipe_tags',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество должно быть равно 1 или больше.')], verbose_name='Количество в рецепте')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='api.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='api.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Ингредиент рецепта',
                'verbose_name_plural': 'Ингредиенты рецептов',
                'db_table': 'cookbook_recipe_ingredients',
                'abstract': False,
                'default_related_name': 'recipe_ingredients',
            },
        ),
        migrations.CreateModel(
            name='RecipeFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', api.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to=settings.AUTH_USER_MODEL, verbose_name='Владелец корзины покупок')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to='api.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'db_table': 'cookbook_recipe_favorite',
                'abstract': False,
                'default_related_name': 'recipe_favorite',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='api.RecipeIngredients', to='api.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', through='api.RecipeTags', to='api.Tag'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipefavorite',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_recipe_favorite'),
        ),
    ]
