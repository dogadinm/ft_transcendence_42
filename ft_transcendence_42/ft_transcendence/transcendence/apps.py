from django.apps import AppConfig


class TranscendenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcendence'

    # def ready(self):
    #     import transcendence.signals

