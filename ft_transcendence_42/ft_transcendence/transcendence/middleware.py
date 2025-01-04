from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            user.last_activity = now()
            user.save()

        return self.get_response(request)