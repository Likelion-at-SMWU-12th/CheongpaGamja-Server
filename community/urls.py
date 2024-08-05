from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColumnViewSet

router = DefaultRouter()
router.register(r'columns', ColumnViewSet, basename='column')

urlpatterns = [
    path('', include(router.urls)),
]