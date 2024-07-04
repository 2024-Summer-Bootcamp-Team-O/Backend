# Generated by Django 5.1a1 on 2024-07-04 07:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='character',
            fields=[
                ('character_id', models.AutoField(primary_key=True, serialize=False)),
                ('character_name', models.CharField(max_length=20)),
                ('character_script', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='episode_time',
            fields=[
                ('time_id', models.AutoField(primary_key=True, serialize=False)),
                ('episode_time', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='work',
            fields=[
                ('worker_id', models.AutoField(primary_key=True, serialize=False)),
                ('worker_location', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='episode',
            fields=[
                ('episode_id', models.AutoField(primary_key=True, serialize=False)),
                ('episode_content', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('episode_time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.episode_time')),
            ],
        ),
        migrations.CreateModel(
            name='chat_room',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('result', models.CharField(blank=True, max_length=2000, null=True)),
                ('mz_percent', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.character')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.member')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.work')),
            ],
        ),
    ]
