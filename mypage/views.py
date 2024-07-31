from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from django.db.models import Count
from mentoring.models import *
from .models import *
from .serializers import * 

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
            "name": user.name,
            "mentoringRecord": mentoringRecord,
            "myMentoring": myMentoring,
            "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
    
    # 멘티 정보 추가
    else:
        # chatrooms = Chatroom.objects.filter(mentee=user.mentee)
        myMentoring = MyChatRoomSerializer(chatrooms, many=True).data
        latest_concern = Concern.objects.filter(author=user.mentee).order_by('-created_at').first()
        data = {
            "info": MenteeSerializer(user.mentee).data,
            "name": user.name,
            "concerns": MyConcernSerializer(latest_concern).data,
            "mentoringRecord": mentoringRecord,
            "myMentoring": myMentoring,
            "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
    
    return Response(data)

@api_view(['GET'])
def my_concerns(request):
    user = request.user
    
    if not user.is_mentor:
        # 고민 최신순 정렬
        myConcerns = Concern.objects.filter(author=user.mentee).order_by('-created_at')
        serializer = MyConcernSerializer(myConcerns, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)
    else:
        return Response({"error" : "현재 사용자가 멘티가 아닙니다."})

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