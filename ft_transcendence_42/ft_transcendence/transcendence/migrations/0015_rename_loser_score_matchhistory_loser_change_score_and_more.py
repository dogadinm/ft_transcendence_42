# Generated by Django 5.1.4 on 2024-12-15 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcendence', '0014_matchhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchhistory',
            old_name='loser_score',
            new_name='loser_change_score',
        ),
        migrations.RenameField(
            model_name='matchhistory',
            old_name='winner_score',
            new_name='loser_match_score',
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='winner_change_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='winner_match_score',
            field=models.IntegerField(default=0),
        ),
    ]