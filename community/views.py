# community/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Column
from .serializers import ColumnSerializer, ColumnCreateSerializer
from users.models import Mentor

class ColumnViewSet(viewsets.ModelViewSet):
  queryset = Column.objects.all()
  serializer_class = ColumnSerializer

  def get_serializer_class(self):
    if self.action == 'create':
      return ColumnCreateSerializer
    return ColumnSerializer

  def perform_create(self, serializer):
    mentor = Mentor.objects.get(user=self.request.user)
    serializer.save(author=self.request.user)

  def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
      return [permissions.IsAuthenticated(), IsMentor()]
    return [permissions.AllowAny()]

  @action(detail=True, methods=['post'])
  def like(self, request, pk=None):
    column = self.get_object()
    user = request.user
    if column.likes.filter(id=user.id).exists():
      column.likes.remove(user)
      return Response({'status': 'unliked'})
    else:
      column.likes.add(user)
      return Response({'status': 'liked'})

  @action(detail=True, methods=['post'])
  def scrap(self, request, pk=None):
    column = self.get_object()
    user = request.user
    if column.scraps.filter(id=user.id).exists():
      column.scraps.remove(user)
      return Response({'status': 'unscraped'})
    else:
      column.scraps.add(user)
      return Response({'status': 'scraped'})

class IsMentor(permissions.BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated and hasattr(request.user, 'mentor')