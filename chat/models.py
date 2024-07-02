from django.db import models
from user.models import User


class Character(models.Model):
    character_id = models.AutoField(primary_key=True)
    character_name = models.CharField(max_length=20)
    character_script = models.CharField(max_length=1000)

    def __str__(self):
        return self.character_name


class Work(models.Model):
    worker_id = models.AutoField(primary_key=True)
    worker_location = models.CharField(max_length=2)

    def __str__(self):
        return self.worker_location


class EpisodeTime(models.Model):
    time_id = models.AutoField(primary_key=True)
    episode_time = models.CharField(max_length=200)

    def __str__(self):
        return str(self.time_id)


class Episode(models.Model):
    episode_id = models.AutoField(primary_key=True)
    episode_content = models.CharField(max_length=200)
    episode_time = models.ForeignKey(EpisodeTime, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.episode_id)


class ChatRoom(models.Model):
    room_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    result = models.CharField(max_length=2000, null=True, blank=True)
    mz_rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.room_id)


class ChatEpi(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("room", "episode")

    def __str__(self):
        return f"{self.room}, {self.episode}"
