# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CustomTokenObtainPairView, LogoutView, GetUserIdView, ResetUserPasswordView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 엔드포인트
    path('logout/', LogoutView.as_view(), name='logout'),  # 로그아웃 엔드포인트
    path('get-user-id/', GetUserIdView.as_view(), name='get-user-id'),
    path('reset-user-pw/', ResetUserPasswordView.as_view(), name = 'reset-user-pw')
]
