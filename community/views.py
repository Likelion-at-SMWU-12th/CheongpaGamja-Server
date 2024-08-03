# community/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Column
from .serializers import ColumnSerializer, ColumnCreateSerializer, UserProfileSerializer
from users.models import Mentor

class ColumnViewSet(viewsets.ModelViewSet):
  queryset = Column.objects.prefetch_related('likes', 'scraps', 'categories').select_related('author').all()
  serializer_class = ColumnSerializer
  @action(detail=True, methods=['get'])
  def author_profile(self, request, pk=None):
    column = self.get_object()
    user = column.author
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

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

  def get_is_scraped(self, obj):
    request = self.context.get('request')
    if request and request.user.is_authenticated:
      return obj.scraps.filter(id=request.user.id).exists()
    return False
  
  @action(detail=True, methods=['post'])
  def scrap(self, request, pk=None):
    column = self.get_object()
    user = request.user
    if column.scraps.filter(id=user.id).exists():
      column.scraps.remove(user)
      is_scraped = False
    else:
      column.scraps.add(user)
      is_scraped = True
    
    # 칼럼 객체를 새로 가져와 시리얼라이즈
    column = self.get_object()  # 이 줄을 추가
    serializer = self.get_serializer(column)
    return Response({
      'status': 'scraped' if is_scraped else 'unscraped',
      'is_scraped': is_scraped,
      'column': serializer.data  # 전체 칼럼 데이터를 포함
    })
    
class IsMentor(permissions.BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated and hasattr(request.user, 'mentor')