from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



@receiver(user_logged_in)
def broadcast_user_online(sender, request, user, **kwargs):
    user.is_online = True
    user.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "status_updates",  # Group name
        {
            "type": "user_status",
            "username": user.username,
            "is_online": user.is_online ,
        },
    )

@receiver(user_logged_out)
def broadcast_user_offline(sender, request, user, **kwargs):
    user.is_online = False
    user.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "status_updates",  # Group name
        {
            "type": "user_status",
            "username": user.username,
            "is_online": user.is_online,
        },
    )