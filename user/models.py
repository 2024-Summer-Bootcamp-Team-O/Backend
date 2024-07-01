from django.db import models


class User(models.Model):
    usernumber = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.username

