# Generated by Django 5.1.4 on 2024-12-17 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0015_rename_loser_score_matchhistory_loser_change_score_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='photo',
            field=models.ImageField(blank=True, default='profile_photos/profile_standard.jpg', null=True, upload_to='profile_photos/'),
        ),
    ]
