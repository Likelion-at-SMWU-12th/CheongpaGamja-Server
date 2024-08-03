from django.db import models
from django.conf import settings
from users.models import *

class Column(models.Model):
  title = models.CharField(max_length=15) # 프론트랑 제목 최대 길이 의논해보기
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='columns') # related_name이 필요할까?
  published_date = models.DateTimeField(auto_now_add=True)
  content = models.TextField()
  image = models.ImageField(upload_to='column_images/', null=True, blank=True)
  categories = models.ManyToManyField(Interest,related_name='columns')
  likes = models.ManyToManyField(User, related_name='liked_columns', blank=True)
  scraps = models.ManyToManyField(User, related_name='scraped_columns', blank=True)
  
  def __str__(self):
    return f"Column({self.id}): {self.title}"