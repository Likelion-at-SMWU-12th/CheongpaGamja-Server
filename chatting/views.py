from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from mentoring.models import *
from .models import *
from .serializers import * 
from django.db.models import Count

    
class ChattingViewSet(viewsets.ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    # 나의 채팅방 목록 조회
    def list(self, request):
        user = request.user
        if user.is_mentor:
            chatrooms = Chatroom.objects.filter(mentor=user.mentor)
        else:
            chatrooms = Chatroom.objects.filter(mentee=user.mentee)
        
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 채팅방 생성
    def create(self, request):
        user = request.user
        data = request.data

        if user.is_mentor:
            return Response({"현재 사용자가 멘티가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        mentee = get_object_or_404(Mentee, user=user)
        mentor = get_object_or_404(Mentor, pk=data.get('mentorId'))
        interests = data.get('interests')
        title = data.get('title')
        
        if not interests or not title:
            return Response({"error": "interest와 title 모두 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the chatroom
        chatroom = Chatroom.objects.create(
            mentor=mentor,
            mentee=mentee,
            title=title
        )

        for interest_id in interests:
            interest = get_object_or_404(Interest, pk=interest_id)
            ChatInterest.objects.create(chatroom=chatroom, interest=interest)
        
        serializer = ChatRoomSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_201_CREATED)   

    # 특정 채팅방에 대한 메시지 생성
    @action(detail=True, methods=['POST'], url_path='add-chat')
    def add_chat(self, request, pk=None):
        chatroom = get_object_or_404(Chatroom, pk=pk)

        if request.user.is_mentor:
            is_mentee = False
        else:
            is_mentee = True

        data = {
            'room': chatroom.id,
            'message': request.data.get('message'),
            'is_mentee': is_mentee
        }

        serializer= ChatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def my_page(request):
    user = request.user

    # 멘토링 내역
    if user.is_mentor:
        chatrooms = Chatroom.objects.filter(mentor=user.mentor)
    else:
        chatrooms = Chatroom.objects.filter(mentee=user.mentee)

    chatCount = chatrooms.values('interests__name').annotate(count=Count('id'))

    chatCountDict = {record['interests__name']: record['count'] for record in chatCount}
    mentoringRecord = []
    for code, name in Interest.INTEREST_CHOICES:
        mentoringRecord.append({
            'interest': name,
            'count': chatCountDict.get(code, 0)
        })
    
    # 일지 목록
    myLogs = Log.objects.filter(author=user)

    # 멘토 정보 추가
    if user.is_mentor:
        # chatrooms = Chatroom.objects.filter(mentor=user.mentor)
        myMentoring = MyChatRoomSerializer(chatrooms, many=True).data
        data = {
            "info": MentorSerializer(user.mentor).data,
            "mentoringRecord": mentoringRecord,
            "myMentoring": myMentoring,
            "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
    
    else:
        # chatrooms = Chatroom.objects.filter(mentee=user.mentee)
        myMentoring = MyChatRoomSerializer(chatrooms, many=True).data
        concerns = Concern.objects.filter(author=user.mentee)
        myMentors = MentorSerializer(user.mentee.liked_mentors.all(), many=True).data
        data = {
            "info": MenteeSerializer(user.mentee).data,
            "concerns": MyConcernSerializer(concerns, many=True).data,
            "mentoringRecord": mentoringRecord,
            "myMentoring": myMentoring,
            "myMentor": myMentors,
            "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
    
    return Response(data)

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = MyLogSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        logs = Log.objects.filter(author=user)

        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user = request.user
        data = request.data
        
        chatroom = get_object_or_404(Chatroom, pk=data.get('chatroomId'))

        log = Log.objects.create(
            title=data.get('title'),
            content=data.get('content'),
            author=user,
            chatroom=chatroom
        )

        serializer = LogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 

