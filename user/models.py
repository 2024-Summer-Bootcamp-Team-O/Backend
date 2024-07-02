from django.db import models


class User(models.Model):
    user_number = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.user_name
