# Generated by Django 3.2.3 on 2024-09-21 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_recipe_short_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(default='MI9w7lbkNpTB', max_length=6, unique=True, verbose_name='Короткая ссылка'),
        ),
    ]
