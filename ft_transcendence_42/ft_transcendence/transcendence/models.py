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


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    player1 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='player1', null=True, blank=True)
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='player2', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name