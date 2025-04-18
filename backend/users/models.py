from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram.constants import (USER_EMAIL_MAX_LENGTH,
                                USER_MAX_LENGTH, USER_REGEX)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(max_length=USER_EMAIL_MAX_LENGTH, unique=True,
                              verbose_name="Электронная почта")
    first_name = models.CharField(max_length=USER_MAX_LENGTH,
                                  verbose_name="Имя")
    last_name = models.CharField(max_length=USER_MAX_LENGTH,
                                 verbose_name="Фамилия", )
    avatar = models.ImageField(upload_to='avatars/', blank=True,
                               null=True, verbose_name="Фото профиля")
    username = models.CharField(max_length=USER_MAX_LENGTH, unique=True,
                                verbose_name="Имя пользователя",
                                validators=[RegexValidator(
                                    regex=USER_REGEX,
                                    message='Имя пользователя некорректно.')])

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
