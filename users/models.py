# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
  is_mentor = models.BooleanField(default=False)
  profile_pic = models.ImageField(upload_to='profile_pics/', default = 'default.png') # profile_pic dir 만들기, default이미지 업로드하기, 사진 첨부 루트 만들기
  name = models.CharField(max_length=50, verbose_name= ("이름"))
  birth_date = models.DateField(verbose_name= ("생년월일"), null=True, blank=True)
  agreed_to_terms = models.BooleanField(default=False, verbose_name= ("이용약관 동의"))
  @property
  def role(self):
    return "Mentor" if self.is_mentor else "Mentee"

class Interest(models.Model):
  INTEREST_CHOICES = (
    ('belief', '가치관'),
    ('finance', '재테크'),
    ('love', '사랑'),
    ('daily', '생활 지식'),
    ('relationship', '인간 관계'),
    ('career', '진로'),
  )
  name = models.CharField(max_length=20, choices=INTEREST_CHOICES, unique=True)

  def __str__(self):
    return self.get_name_display()

class Mentor(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor')
  interests = models.ManyToManyField(Interest, through='MentorInterest')
  rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  total_ratings = models.PositiveIntegerField(default=0)
  
  # 모델 레벌의 유효성 검사는 데이터베이스에 저장되기 전 최종적으로 데이터 유효성 보장
  # 데이터가 어떤 방법으로 저장되기 전에 항상 이 검사를 통과
  def clean(self):
    super().clean()
    if self.interests.count() > 3:
        raise ValidationError("멘토는 3개 이하의 관심사를 선택할 수 있습니다.")
  def update_rating(self, new_rating):
    self.rating = ((self.rating * self.total_ratings) + new_rating) / (self.total_ratings + 1)
    self.total_ratings += 1
    self.save()

class MentorInterest(models.Model):
  mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
  interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
  
  class Meta:
    unique_together = ('mentor', 'interest')
  def __str__(self):
    return f'{self.mentor.user.username} - {self.interest.name}'

class Mentee(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentee')
  interests = models.ManyToManyField(Interest, through='MenteeInterest')
  def clean(self):
    super().clean()
    if self.interests.count() > 5:
        raise ValidationError("멘티는 5개 이하의 관심사를 선택할 수 있습니다.")

class MenteeInterest(models.Model):
  mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
  interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
  
  class Meta:
    unique_together = ('mentee', 'interest')
  def __str__(self):
    return f'{self.mentee.user.username} - {self.interest.name}'