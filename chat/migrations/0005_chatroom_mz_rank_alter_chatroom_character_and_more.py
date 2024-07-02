# Generated by Django 5.1a1 on 2024-07-02 13:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_chatroom_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='mz_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='character',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.character'),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='result',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
