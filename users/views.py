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

from django.contrib.auth.hashers import make_password
import random
import string

class GetUserIdView(APIView):
  permission_classes = [AllowAny]
  def get(self, request):
    name = request.query_params.get('name')
    email = request.query_params.get('email')
    
    if not name or not email:
      return Response({"error": "회원 이름과 이메일을 모두 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    User = get_user_model()
    try:
      user = User.objects.get(name=name, email=email)
      return Response({"username": user.username})
    except User.DoesNotExist:
      return Response({"error": "회원이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

class ResetUserPasswordView(APIView):
  permission_classes = [AllowAny]

  def get(self, request):
    # 사용자 이름과 이메일을 쿼리 매개변수로 받습니다.
    username = request.query_params.get('username')
    email = request.query_params.get('email')

    # 필수 매개변수가 없을 경우 오류 응답 반환
    if not username or not email:
      return Response({"error": "사용자 이름과 이메일을 모두 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    try:
      # 사용자 모델에서 해당하는 사용자 찾기
      user = User.objects.get(username=username, email=email)

      # 임시 비밀번호 생성
      new_password = self.generate_temp_password()
      
      # 비밀번호 변경
      user.password = make_password(new_password)  # 해시 비밀번호로 저장
      user.save()

      # 비밀번호 변경 성공 메시지와 임시 비밀번호 반환
      return Response({"message": "비밀번호가 초기화되었습니다.", "new_password": new_password}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
      # 사용자가 존재하지 않을 경우 오류 응답 반환
      return Response({"error": "해당 사용자 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

  def generate_temp_password(self, length=12):
    """임시 비밀번호 생성"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
  
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
  def get_queryset(self):
    return User.objects.prefetch_related(
      'mentor',
      'mentor__interests',
      'mentee'
    )
  def get_permissions(self):
    if self.action == 'create':
      permission_classes = [AllowAny]
    else:
      permission_classes = [IsAuthenticated]
    return [permission() for permission in permission_classes]

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    headers = self.get_success_headers(serializer.data)
    
    # Re-fetch the user to get the full data including related profiles
    user = User.objects.prefetch_related(
        'mentor', 'mentor__interests', 'mentee'
    ).get(id=user.id)
    response_serializer = self.get_serializer(user)
    
    response_data = response_serializer.data
    response_data['message'] = "User created successfully!"
    
    return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
  
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