from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone

class Concern(models.Model):
    author = models.ForeignKey('users.Mentee', on_delete=models.CASCADE)
    interests = models.ManyToManyField('users.Interest', through='ConcernInterest')
    content = models.CharField(verbose_name='한 줄 고민', max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.author.user.name}의 고민 / 내용: {self.content}'
    
class ConcernInterest(models.Model):
    concern = models.ForeignKey(Concern, on_delete=models.CASCADE)
    interest = models.ForeignKey('users.Interest', on_delete=models.CASCADE)

class Comment(models.Model):
    concern = models.ForeignKey(Concern,related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('users.Mentor', on_delete=models.CASCADE)
    content = models.TextField(verbose_name="고민 답변", max_length=200)

    def __str__(self):
        return f'{self.author.user.name}의 고민에 대한 답변'
