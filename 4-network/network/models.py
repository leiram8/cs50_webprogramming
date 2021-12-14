from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    text = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True)

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ManyToManyField(User, blank=True, related_name="followee")

