"""
ASGI config for ft_transcendence project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
# from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import transcendence.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ft_transcendence.settings")
django.setup()

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            transcendence.routing.websocket_urlpatterns
        )
    ),
})

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import timedelta
from django.utils.timezone import now
from threading import Thread
import asyncio
from transcendence.models import User
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import get_user_model

from django.utils import timezone

User = get_user_model()


async def check_user_activity():
    while True:
        await asyncio.sleep(15)
        inactive_users = await sync_to_async(get_inactive_users)()
        all_users = await sync_to_async(get_all_users)()

        for user in inactive_users:
            user.is_online = False
            await sync_to_async(user.save)()


        for user in all_users:
            if user not in inactive_users:
                user.is_online = True
                await sync_to_async(user.save)()





def get_all_users():
    return list(User.objects.all())

def get_inactive_users():
    return list(
        User.objects.filter(
            last_activity__lt=timezone.now() - timedelta(minutes=5),
        )
    )

# Start the background task
def start_background_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_user_activity())

# Create and start the thread for the background task
thread = Thread(target=start_background_task, daemon=True)
thread.start()