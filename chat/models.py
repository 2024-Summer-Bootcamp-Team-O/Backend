from django.db import models

from user.models import User


class Character(models.Model):
    characterid = models.AutoField(primary_key=True)
    charactername = models.CharField(max_length=20)

    def __str__(self):
        return self.charactername


class Work(models.Model):
    workerid = models.AutoField(primary_key=True)
    workerlocation = models.CharField(max_length=2)

    def __str__(self):
        return self.workerlocation


class EpisodeTime(models.Model):
    timeid = models.AutoField(primary_key=True)
    episodetime = models.CharField(max_length=200)

    def __str__(self):
        return self.timeid


class Episode(models.Model):
    episodeid = models.AutoField(primary_key=True)
    episodecontent = models.CharField(max_length=200)
    episodetime = models.ForeignKey(EpisodeTime, on_delete=models.CASCADE)

    def __str__(self):
        return self.episodeid


class ChatRoom(models.Model):
    roomid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    def __str__(self):
        return self.roomid


class ChatEpi(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('room', 'episode')

    def __str__(self):
        return f"{self.room}, {self.episode}"

