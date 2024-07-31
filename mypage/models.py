from django.db import models
from chatting.models import Chatroom
from django.utils import timezone
from users.models import *
from chatting.models import *

class Log(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
