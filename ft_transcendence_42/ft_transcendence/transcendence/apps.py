from django.apps import AppConfig
import threading
import logging

logger = logging.getLogger(__name__)

def create_bot_user():
    """Creates the bot user when the server starts."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        bot_user, created = User.objects.get_or_create(
            username="chatbot",
            defaults={"is_active": True, "email": "bot@example.com"}
        )
        if created:
            logger.info("Bot user created successfully.")
            print("Bot user created successfully.")
        else:
            print("Bot user already exists.")
            logger.info("Bot user already exists.")
    except Exception as e:
        logger.error(f"Error creating bot user: {e}")

class TranscendenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcendence'

    def ready(self):
        """Run bot creation in a separate thread to avoid database access issues."""
        threading.Thread(target=create_bot_user, daemon=True).start()

