# Generated by Django 5.1.3 on 2024-12-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0005_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
