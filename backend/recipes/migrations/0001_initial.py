# Generated by Django 3.2.3 on 2024-01-10 10:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Рецепт - пользователь',
                'verbose_name_plural': 'Рецепт - пользователь',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название ингредиента', max_length=200, unique=True, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(help_text='Укажите единицы измерения', max_length=200, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('id', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_favorited', models.BooleanField(default=True, help_text='Отметьте рецепт в избранное', verbose_name='Находится в избранном')),
                ('is_in_shopping_cart', models.BooleanField(default=True, help_text='Отложите рецепт в корзину', verbose_name='Находится в корзине')),
                ('image', models.ImageField(help_text='Укажите изображение рецепта', upload_to='recipes_images', verbose_name='Изображение рецепта')),
                ('name', models.CharField(help_text='Укажите название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('text', models.TextField(help_text='Укажите описание рецепта', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Укажите время приготовления, от 1 мин', validators=[django.core.validators.MinValueValidator(1, 'Минимальное время приготовления'), django.core.validators.MaxValueValidator(32000, 'Максимальное время приготовления')], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Укажите кол-во ингредиента, от 1 и более', validators=[django.core.validators.MinValueValidator(1, 'Минимальное кол-во ингредиента'), django.core.validators.MaxValueValidator(32000, 'Максимальное кол-во ингредиента')], verbose_name='Кол-во ингредиента')),
            ],
            options={
                'verbose_name': 'Ингредиент - рецепта',
                'verbose_name_plural': 'Ингредиент - рецепта',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Тег - рецепта',
                'verbose_name_plural': 'Тег - рецепта',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название тега', max_length=200, unique=True, verbose_name='Название тега')),
                ('color', models.CharField(help_text='Укажите цвет в HEX (пример ввода: #E26C2D)', max_length=7, null=True, unique=True, validators=[django.core.validators.RegexValidator('^#[0-9A-F]{6}$', 'Поддерживаемые знаки.')], verbose_name='Цвет')),
                ('slug', models.SlugField(help_text='Укажите аббревиатуру тега', max_length=200, null=True, unique=True, verbose_name='Аббревиатура тега')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Укажите название рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcarts', to='recipes.recipe', verbose_name='Название рецепта')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Список покупок',
                'ordering': ('recipe',),
            },
        ),
    ]
