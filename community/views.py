# community/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Column
from .serializers import ColumnSerializer, ColumnCreateSerializer, UserProfileSerializer
from users.models import Mentor

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from django.db.models import Q
from rest_framework.filters import SearchFilter

@method_decorator(never_cache, name='dispatch')
class ColumnViewSet(viewsets.ModelViewSet):
  queryset = Column.objects.prefetch_related('likes', 'scraps', 'categories').select_related('author').all()
  serializer_class = ColumnSerializer
  
  # 제목 검색 기능 추가
  filter_backends = [SearchFilter]
  search_fields = ['title']
  
  def get_queryset(self):
    queryset = Column.objects.all().select_related('author').prefetch_related('scraps', 'likes', 'categories')
    search_query = self.request.query_params.get('search', None)
    if search_query:
      queryset = queryset.filter(Q(title__icontains=search_query))
    return queryset
  
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
    
  @action(detail=False, methods=['get'], url_path='mentor')
  def mentor_columns(self, request):
    mentor_id = request.query_params.get('mentor_id')
    if not mentor_id:
      return Response({"error": "mentor_id is required"}, status=400)
    
    try:
      mentor = Mentor.objects.get(id=mentor_id)
    except Mentor.DoesNotExist:
      return Response({"error": "Mentor not found"}, status=404)
    
    columns = self.get_queryset().filter(author_id=mentor.user_id)
    serializer = self.get_serializer(columns, many=True)
    return Response(serializer.data)

  # form-data 전송 시 Int 카테고리
  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    
    # Re-serialize the created object with ColumnSerializer
    output_serializer = ColumnSerializer(serializer.instance, context={'request': request})
    return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class IsMentor(permissions.BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated and hasattr(request.user, 'mentor')