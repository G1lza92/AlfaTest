from django.db import models


class User(models.Model):
    login = models.CharField(
        max_length=50,
        unique=True,
    )
    fio = models.TextField(
        max_length=300,
        verbose_name='ФИО',
    )

    def __str__(self):
        return self.login
