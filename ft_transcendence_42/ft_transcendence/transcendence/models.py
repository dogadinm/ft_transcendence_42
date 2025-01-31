from django.db import models
import os
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import make_password
import logging
from django.utils.timezone import now
from django.db import models
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager

class User(AbstractUser):
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True, default="profile_photos/profile_standard.jpg")
    blocked_users = models.ManyToManyField('self', blank=True, related_name='blocking_users', symmetrical=False)
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=now)
    lobby = models.CharField(max_length=30, blank=True, null=True)
    user_42 = models.BooleanField(default=False)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    wallet_prt_key = models.CharField(max_length=150, blank=True, null=True)
    tournament_nickname = models.CharField(max_length=30, blank=True, null=True, unique=True)


    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = User.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.photo != self.photo:
                old_photo = old_instance.photo
                try:
                    if old_photo and os.path.isfile(old_photo.path) and old_photo.name != settings.DEFAULT_PROFILE_PHOTO:
                        os.remove(old_photo.path)
                except Exception as e:
                    logging.error(f"Error deleting old photo: {e}")

        super(User, self).save(*args, **kwargs)




class Score (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"User: {self.user.username}, Score: {self.score}"

class ScoreDoubleJack (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doublejack_scores")
    score = models.IntegerField(default=1000)
    def __str__(self):
        return f"User: {self.user.username}, ScoreDoubleJack: {self.score}"

class MatchHistory (models.Model):
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner")
    loser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loser")
    winner_match_score = models.IntegerField(default=0)
    loser_match_score = models.IntegerField(default=0)
    winner_change_score = models.IntegerField(default=0)
    loser_change_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Match: {self.winner.username}-{self.loser.username}:{self.winner_match_score}-{self.loser_match_score}"

class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                name='unique_friend_request_direct'
            ),
            models.UniqueConstraint(
                name='unique_friend_request_inverse',
                condition=Q(sender__lt=models.F('receiver')),  # Гарантия уникальности в обе стороны
                fields=['sender', 'receiver']
            ),
        ]

class Friend(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friends_list')
    friends = models.ManyToManyField(User, related_name='friends_of', blank=True)
    def __str__(self):
        return self.owner.username

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.sender.username}-{self.receiver.username}"

class ChatGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True, default="profile_photos/profile_standard.jpg")
    
    members = models.ManyToManyField(User, related_name='chats', symmetrical=False)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Message(models.Model):
    chat = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chat.name


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    player1 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='player1', null=True, blank=True)
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='player2', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name