from django.contrib import admin
from .models import User, Score, Friend, PrivateMessage, FriendRequest, MatchHistory
from django import forms

# Register your models here.
admin.site.register(User)
admin.site.register(Score)
admin.site.register(Friend)
admin.site.register(PrivateMessage)
admin.site.register(FriendRequest)
admin.site.register(MatchHistory)