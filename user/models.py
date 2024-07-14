from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class user(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name",
    ]

    def __str__(self):
        return self.name
