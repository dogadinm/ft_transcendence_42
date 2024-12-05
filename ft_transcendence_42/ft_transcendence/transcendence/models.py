from django.db import models
# from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Score (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"User: {self.user.username}, Score: {self.score}"

class Friend(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friends_list')
    friends = models.ManyToManyField(User, related_name='friends_of', blank=True)
    def __str__(self):
        return self.owner.username

class ChatGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_chats')
    members = models.ManyToManyField(User, related_name='chats')

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