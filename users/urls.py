# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MentorViewSet, MenteeViewSet, InterestReadOnlyViewSet

router = DefaultRouter()
router.register(r'register', UserViewSet, basename='user')
router.register(r'mentors', MentorViewSet, basename='mentor')
router.register(r'mentees', MenteeViewSet, basename='mentee')
router.register(r'interests', InterestReadOnlyViewSet, basename='interest')

urlpatterns = [
    path('', include(router.urls)),
]
