from django.db import models
from django.conf import settings


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Название ингредиента")
    measurement_unit = models.CharField(
        max_length=64, verbose_name="Единицы измерения")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recipes', verbose_name="Автор"
    )
    name = models.CharField(max_length=256, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name="Фото рецепта")
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления")
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='recipes'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE, verbose_name="Рецепт")
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE, verbose_name="Ингредиент")
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        unique_together = ('recipe', 'ingredient')


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorites', verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorited_by', verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} избранное: {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_carts', verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} в списке покупок: {self.recipe}'
