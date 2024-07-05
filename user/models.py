from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class user(AbstractBaseUser):
    user_email = models.EmailField(max_length=100, unique=True)
    user_name = models.CharField(max_length=100)
    user_password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "user_email"
    REQUIRED_FIELDS = ["user_name", ]

    def __str__(self):
        return self.user_name
