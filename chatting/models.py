from django.db import models
from users.models import *
from mentoring.models import *
from django.utils import timezone

class Chatroom(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Interest, through='ChatInterest')
    title = models.CharField(max_length=20)

class ChatInterest(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)

class Chat(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    is_mentee = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

class Log(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)