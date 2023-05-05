from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    friends = models.ManyToManyField(
        "users.User",
        related_name="+",
        verbose_name="Друзья",
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username
