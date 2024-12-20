# Generated by Django 5.1.3 on 2024-12-05 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='friend',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='friend',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends_of', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='friend',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='friends_list', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='friend',
            name='friend',
        ),
    ]
