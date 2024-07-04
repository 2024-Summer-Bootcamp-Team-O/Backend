from django.db import models


class member(models.Model):
    member_id = models.AutoField(primary_key=True)
    member_email = models.CharField(max_length=100)
    member_name = models.CharField(max_length=100)
    member_password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.member_name
