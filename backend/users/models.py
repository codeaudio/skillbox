from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE

from users.validators import password_validator, username_validator


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        verbose_name='username',
        max_length=30,
        validators=[username_validator]
    )
    email = models.EmailField(
        unique=True,
        null=False,
        verbose_name='адрес почты'
    )
    first_name = models.CharField(
        null=True,
        max_length=35,
        blank=True,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        null=True,
        max_length=35,
        blank=True,
        verbose_name='Фамилия пользователя',
    )
    password = models.CharField(
        max_length=90,
        verbose_name='Пароль пользователя',
        validators=[password_validator]
    )
    is_confirm = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password')

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return self.email


class AuthCode(models.Model):
    user = models.OneToOneField(
        User, related_name='codes', on_delete=CASCADE
    )
    code = models.IntegerField()
    exp = models.DateTimeField()

    class Meta:
        db_table = 'auth_code'
        verbose_name = 'Авторизационный код'
        verbose_name_plural = 'Авторизационные коды'
        ordering = ['-id']

    def __str__(self):
        return str(self.user)


class ConfirmCode(models.Model):
    user = models.OneToOneField(
        User, related_name='confirms', on_delete=CASCADE
    )
    code = models.CharField(max_length=32)

    class Meta:
        db_table = 'confirm_code'
        verbose_name = 'Код подтверждения пользователя'
        verbose_name_plural = 'Коды подтверждения пользователя'
        ordering = ['-id']

    def __str__(self):
        return str(self.user)
