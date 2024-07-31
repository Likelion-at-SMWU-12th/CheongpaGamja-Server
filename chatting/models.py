from django.db import models
from mentoring.models import *
from django.utils import timezone
from users.models import *

class Chatroom(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    mentor_response = models.BooleanField(default=False)
    interests = models.ManyToManyField(Interest, through='ChatInterest')
    title = models.CharField(max_length=20)

class ChatInterest(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    interest = models.ForeignKey('users.Interest', on_delete=models.CASCADE)

class Chat(models.Model):
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    is_mentee = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)