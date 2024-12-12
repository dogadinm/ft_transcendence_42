from django.contrib import admin
from .models import User, Score, Room, Friend, ChatGroup, Message, PrivateMessage
from django import forms


# Register your models here.
admin.site.register(User)
admin.site.register(Score)
admin.site.register(Room)
admin.site.register(Friend)
admin.site.register(ChatGroup)
admin.site.register(Message)
admin.site.register(PrivateMessage)