from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth import login, logout, authenticate
from users.serializers import *
from users.models import *
from .serializers import *
from .models import *
from django.db.models import Count

@api_view(['GET'])
def home(request):
    if request.user:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response("로그인 상태가 아님")

@api_view(['POST'])
def login_api(request):
    try:
        data = request.data
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            data = {
                'username':username
            }

            return Response(data=data, status=200)
        
        else:
            return Response({"error": "Invalid username or password."})

    except Exception as e:
        print(f"Login error: {e}")
        return Response({"error": "로그인 실패!"}, status=400)

@api_view(['POST'])
def signup_api(request):
    data = request.data
    try:
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        is_mentor = data.get('is_mentor') == 'True'

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            name=name,
            is_mentor=is_mentor,
        )

        if(is_mentor):
            Mentor(user=user).save()
        else:
            Mentee(user=user).save()

        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    except Exception as e:
        print(f"Signup error: {e}")
        return Response({"error": "회원가입 실패!"}, status=400)

# 멘토 추천(매칭 기능)            
@api_view(['POST'])
def matching(request):
    user = request.user
    data = request.data

    if user.is_mentor:
        return Response({"현재 사용자가 멘티가 아닙니다."}, status=400)
    
    interests = data.get('interests')
    if not interests:
        return Response({"error":"interests가 필요합니다."})
    
    mentee_interests = []
    for interest_name in interests:
        interest = Interest.objects.get(name=interest_name)
        mentee_interests.append(interest)

    
    # 설정한 카테고리와 일치하는 '멘토' 추출
    # 카테고리가 많이 일치하는 순대로 정렬
    matching_mentors = Mentor.objects.filter(
        interests__in=mentee_interests
    ).distinct()

    # 별점 순서대로 5명만 보여줌
    matching_mentors = matching_mentors.order_by(
        '-rating'
    )[:5]

    serializer = MentorSerializer(matching_mentors, many=True)
    return Response(serializer.data, status=200)


# 고민 생성(멘티)
class ConcernViewSet(viewsets.ModelViewSet):
    queryset = Concern.objects.all()
    serializer_class = ConcernSerializer
    
    # 고민 목록(멘토에게 보여주기)
    def list(self, request):
        if request.user.is_mentor :
            # 고민에 대한 답변이 4개 이하인 것만 보여주기
            concerns = Concern.objects.annotate(num_comments=Count('comments')).filter(num_comments__lte=4)
            serializer = ConcernViewSerializer(concerns, many=True)
            # serializer = ConcernSerializer(concerns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"현재 사용자가 멘토가 아닙니다"}, status=400)
        
    # 고민 상세 조회
    def retrieve(self, request, *args, **kwargs):
        concern = self.get_object()
        serializer = ConcernViewSerializer(concern)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 고민 생성(멘티가 생성)
    def create(self, request):
        if request.user.is_mentor:
            return Response({"error" : "현재 사용자가 멘티가 아닙니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        interests_data = validated_data.pop('interests')
        content = validated_data['content']
        
        concern = Concern.objects.create(author=request.user.mentee, content=content)
        
        for interest_name in interests_data:
            interest = Interest.objects.get(name=interest_name)
            ConcernInterest.objects.create(concern=concern, interest=interest)
        
        concern_serializer = self.get_serializer(concern)
        return Response(concern_serializer.data, status=status.HTTP_201_CREATED)
    
    # 고민 수정(멘티)
    def update(self, request, *args, **kwargs):
        if request.user.is_mentor:
            return Response({"error": "현재 사용자가 멘티가 아닙니다."}, status=status.HTTP_403_FORBIDDEN)

        concern = self.get_object()

        if concern.author.user != request.user:
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(concern, data=request.data, context={'request': request})

        if serializer.is_valid():
            validated_data = serializer.validated_data
            # interests_data = validated_data.pop('interests', None)
            interests_data = validated_data.get('interests', [])

            serializer.save()

            if interests_data is not None:
                ConcernInterest.objects.filter(concern=concern).delete()

                for interest_name in interests_data:
                    interest = Interest.objects.get(name=interest_name)
                    ConcernInterest.objects.create(concern=concern, interest=interest)

            return Response(ConcernViewSerializer(concern).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 고민에 대한 답변(멘토)
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    def get_queryset(self):
        # 특정 Concern
        concern_id = self.kwargs.get('concern_id')
        if concern_id:
            return Comment.objects.filter(concern_id=concern_id)
        return Comment.objects.all()
    
    # 답변 생성
    def create(self, request, *args, **kwargs):

        if not request.user.is_mentor:
            return Response({"error":"멘토만이 답변을 생성할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        concern_id = self.kwargs.get("concern_id")
        if not concern_id:
            return Response({"error": "고민 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            concern = Concern.objects.get(id=concern_id)
        except Concern.DoesNotExist:
            return Response({"error": "고민이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        data['author'] = request.user.mentor.id
        data['concern'] = concern_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(concern=concern, author=self.request.user.mentor)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
# 멘토 조회
class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer

    # 멘토 목록(멘티에게 보여주기)
    def list(self, request):
        if request.user.is_mentor:
            return Response({"현재 사용자가 멘티가 아닙니다"}, status=400)
        mentors = self.queryset
        serializer = self.get_serializer(mentors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 관심 멘토 설정
@api_view(['POST'])
def likes_mentor(request, mentor_id):
    user = request.user
    if user.is_authenticated:
        if not user.is_mentor:
            mentor = get_object_or_404(Mentor, pk=mentor_id)

            if mentor.like_mentees.filter(pk=user.mentee.id).exists():
                mentor.like_mentees.remove(user.mentee)
                return Response({'멘토 관심 설정이 해제되었습니다.'})
            else:
                mentor.like_mentees.add(user.mentee)
                return Response({'멘토 관심 설정이 완료되었습니다.'})
        else:
            return Response({'현재 사용자가 멘티가 아닙니다.'})
    else:
        return Response({'로그인한 사용자가 없습니다.'})