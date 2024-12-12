# Generated by Django 5.1.3 on 2024-12-08 14:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0009_alter_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='blocked_users',
            field=models.ManyToManyField(blank=True, related_name='blocking_users', to=settings.AUTH_USER_MODEL),
        ),
    ]