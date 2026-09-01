from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("email", unique=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.username
