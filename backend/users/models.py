from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (FIRST_NAME_MAX_LENGTH,
                             LAST_NAME_MAX_LENGTH,
                             USERNAME_MAX_LENGTH)
from users.validators import validate_username


class MyUser(AbstractUser):

    email = models.EmailField('Емейл', unique=True)
    username = models.CharField(
        'Юзернейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(validate_username,),
        error_messages={
            'unique': 'Пользователь с таким юзернеймом уже существует.',
        },
    )
    first_name = models.CharField('Имя', max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_MAX_LENGTH)
    avatar = models.ImageField(
        'Аватарка', upload_to='users', blank=True, null=True)

    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscribtion(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions')
    is_subscribed_to = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Подписан на',
        related_name='subscribers')
    subscription_date = models.DateField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'is_subscribed_to'),
                name='unique_user_is_subscribed_to',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('is_subscribed_to')),
                name='user_cant_follow_self'
            ),
        )
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-subscription_date',)

    def __str__(self):
        return (f'{self.user.username} подписан '
                f'на {self.is_subscribed_to.username}')
