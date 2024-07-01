from django.db import models

from user.models import User
from chat.models import ChatRoom


# Create your models here.
class Result(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.IntegerField()

    class Meta:
        unique_together = ('room', 'user')

    def __str__(self):
        return str(self.result)

