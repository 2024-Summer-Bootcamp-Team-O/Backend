from django.db import models
from user.models import user


class character(models.Model):
    character_id = models.AutoField(primary_key=True)
    character_name = models.CharField(max_length=20)
    character_script = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.character_name


class episode_time(models.Model):
    episode_time_id = models.AutoField(primary_key=True)
    episode_flow = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.time_id)


class episode(models.Model):
    episode_id = models.AutoField(primary_key=True)
    episode_content = models.CharField(max_length=200)
    episode_time = models.ForeignKey(episode_time, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.episode_id)


class chat_room(models.Model):
    room_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    character = models.ForeignKey(character, on_delete=models.CASCADE)
    result = models.CharField(max_length=2000, null=True, blank=True)
    mz_percent = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.room_id)


class chat_episode(models.Model):
    chat_episode_id = models.AutoField(primary_key=True)
    chat_room = models.ForeignKey(chat_room, on_delete=models.CASCADE)
    episode = models.ForeignKey(episode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.chat_episode_id)