from django.shortcuts import render

# 회원가입
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import User, Mentor, Mentee, Interest
from .serializers import UserSerializer, MentorSerializer, MenteeSerializer, InterestSerializer

from rest_framework.permissions import AllowAny

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = [AllowAny]

  def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    if response.status_code == status.HTTP_201_CREATED:
      response.data['message'] = "User created successfully!"
    return response

class MentorViewSet(viewsets.ModelViewSet):
  queryset = Mentor.objects.all()
  serializer_class = MentorSerializer
  permission_classes = [AllowAny]

  def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    if response.status_code == status.HTTP_201_CREATED:
      response.data['message'] = "Mentor created successfully!"
    return response

class MenteeViewSet(viewsets.ModelViewSet):
  queryset = Mentee.objects.all()
  serializer_class = MenteeSerializer
  permission_classes = [AllowAny]

  def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    if response.status_code == status.HTTP_201_CREATED:
      response.data['message'] = "Mentee created successfully!"
    return response

# Interest의 경우 고정되고 더 추가될 일이 없다는 가정하게 읽기만 하는 API로 작성
class InterestReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [AllowAny]
