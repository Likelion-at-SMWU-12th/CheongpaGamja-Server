from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import viewsets, status
from mentoring.models import *
from .models import *
from .serializers import * 
    
class ChattingViewSet(viewsets.ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    # 나의 채팅방 목록 조회
    def list(self, request):
        user = request.user
        if user.is_mentor:
            # chatrooms = Chatroom.objects.filter(mentor=user.mentor)
            recent_chats = Chatroom.objects.filter(mentor=user.mentor, mentor_response=True)
            mentee_suggestions = Chatroom.objects.filter(mentor=user.mentor, mentor_response=False)
            return Response({
                "recent_chats" : ChatRoomSerializer(recent_chats, many=True).data,
                "mentee_suggestions" : ChatRoomSerializer(mentee_suggestions, many=True).data
            })
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
            if not chatroom.mentor_response:
                chatroom.mentor_response = True
                chatroom.save()
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
    
    @action(detail=False, methods=['GET'], url_path='my-mentors')
    def my_mentors(self, request):
        user = request.user

        if user.is_mentor:
            return Response({"error : 현재 사용자가 멘티가 아닙니다"})
        else:
            myMentors = MentorSerializer(user.mentee.liked_mentors.all(), many=True).data
            if myMentors:
                return Response(myMentors, status=status.HTTP_200_OK)          
            else:
                return Response({"현재 관심 설정한 멘토가 없습니다."}) 