"""
URL configuration for voyage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from mentoring.views import *
from rest_framework.routers import DefaultRouter
from chatting.views import *
from users.views import *
from mypage.views import *

# ImageField를 위해
from django.conf import settings
from django.conf.urls.static import static

# 로그인을 위해
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'concerns', ConcernViewSet, basename='concern')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'mentors', MentorViewSet, basename='mentor')
router.register(r'chat', ChattingViewSet, basename='chatting')
router.register(r'log', LogViewSet, basename='log')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 엔드포인트
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신 엔드포인트

    # path('login/', login_api),
    # path('signup/', signup_api),
    # path('', home),
    path('matching/', matching),
    path('', include(router.urls)),
    path('concerns/<int:concern_id>/', include(router.urls)),
    path('my-page/', my_page),
    path('my-page/concerns/', my_concerns),
    path('mentors/<int:mentor_id>/likes/', likes_mentor),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
