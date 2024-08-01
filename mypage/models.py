from django.db import models
from chatting.models import Chatroom
from django.utils import timezone
from users.models import *
from chatting.models import *
from django.utils import timezone

class Log(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

# 멘토링 리뷰
class Review(models.Model):
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(default=timezone.now)
