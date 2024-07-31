# 회원가입
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import *
from chatting.models import *
from chatting.serializers import *
from mentoring.models import *
from mentoring.serializers import *
from .serializers import UserSerializer, MentorSerializer, MenteeSerializer, InterestSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    data = super().validate(attrs)

    # 사용자에 대한 추가 정보를 JWT 페이로드에 포함
    data['user_id'] = self.user.id
    data['username'] = self.user.username
    data['is_mentor'] = self.user.is_mentor
    data['name'] = self.user.name

    return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 로그아웃 뷰
class LogoutView(APIView):
  permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

  def post(self, request):
    # Refresh 토큰을 요청 데이터에서 추출
    refresh_token = request.data.get("refresh")
    
    if not refresh_token:
      return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
      # RefreshToken 객체 생성 및 블랙리스트에 추가
      token = RefreshToken(refresh_token)
      token.blacklist()
      return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
      return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  def get_permissions(self):
    if self.action == 'create':
      permission_classes = [AllowAny]
    else:
      permission_classes = [IsAuthenticated]
    return [permission() for permission in permission_classes]

  def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    if response.status_code == status.HTTP_201_CREATED:
      response.data['message'] = "User created successfully!"
    return response
  
  # PUT을 통해서 전체 업뎃 (채우지 않은 속성은 초기화됨)
  def update(self, request, *args, **kwargs):
    return self._update_user(request, *args, **kwargs)
  
  # PATCH를 통해서 부분 업뎃
  def partial_update(self, request, *args, **kwargs):
    kwargs['partial'] = True
    return self._update_user(request, *args, **kwargs)

  def _update_user(self, request, *args, **kwargs):
    # 현재 요청하는 사람이 authenticated됐는지
    if not request.user.is_authenticated:
      return Response({"detail": "Authentication credentials were not provided."}, 
        status=status.HTTP_401_UNAUTHORIZED)

    # 본인 프로필 update하려는지 검사
    if int(kwargs.get('pk')) != request.user.id:
      return Response({"detail": "You do not have permission to modify this user."}, 
        status=status.HTTP_403_FORBIDDEN)

    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=partial)
    
    if serializer.is_valid():
      self.perform_update(serializer)
      return Response(serializer.data)
    else:
      print(f"Serializer errors: {serializer.errors}")
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def perform_update(self, serializer):
    serializer.save()
  
  # 유저를 Hard Delete 하자
  def delete(self, request, *args, **kwargs):
    user = self.get_object()

    # 본인 계정만 삭제 가능하도록
    if request.user != user:
      return Response(
        {"detail": "본인 계정만 탈퇴할 수 있습니다."},
        status=status.HTTP_403_FORBIDDEN
      )

    # 멘토/멘티 프로필도 삭제하기
    try:
      if user.is_mentor:
        user.mentor.delete()
      else:
        user.mentee.delete()
    except Exception as e:
      return Response(
        {"detail": f"Error while deleting related profile: {str(e)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

    # 하드 삭제
    user.delete()

    return Response(
      {"detail": "회원 탈퇴가 성공적으로 이루어졌습니다."},
      status=status.HTTP_204_NO_CONTENT
    )