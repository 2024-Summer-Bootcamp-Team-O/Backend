from django.db import models
from user.models import user


class character(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    script = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class voice(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=200)
    character = models.ForeignKey(character, on_delete=models.CASCADE)
    stability = models.FloatField()
    similarity = models.FloatField()
    style = models.FloatField()

    def __str__(self):
        return str(self.id)


class episode_flow(models.Model):
    id = models.AutoField(primary_key=True)
    flow = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class episode(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=200)
    episode_flow = models.ForeignKey(episode_flow, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class chat_room(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    character = models.ForeignKey(character, on_delete=models.CASCADE)
    result = models.CharField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class chat_episode(models.Model):
    id = models.AutoField(primary_key=True)
    chat_room = models.ForeignKey(chat_room, on_delete=models.CASCADE)
    episode = models.ForeignKey(episode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
