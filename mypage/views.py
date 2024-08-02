from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
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

    # 멘토링 내역
    # if user.is_mentor:
    #     chatrooms = Chatroom.objects.filter(mentor=user.mentor)
    # else:
    #     chatrooms = Chatroom.objects.filter(mentee=user.mentee)

    # chatCount = chatrooms.values('interests__name').annotate(count=Count('id'))

    # chatCountDict = {record['interests__name']: record['count'] for record in chatCount}
    # mentoringRecord = []
    # for code, name in Interest.INTEREST_CHOICES:
    #     mentoringRecord.append({
    #         'interest': name,
    #         'count': chatCountDict.get(code, 0)
    #     })
    
    # 일지 목록
    myLogs = Log.objects.filter(author=user)
    myMentoring = MyChatRoomSerializer(chatrooms, many=True).data

    # 멘토 정보 추가
    if user.is_mentor:
        for interest in user.mentor.interests.all():
            mentoringRecord.append({
                'interest': interest.name,
                'count': chatCountDict.get(interest.name, 0)
        })
        
        latest_review = Review.objects.filter(mentor=user.mentor).order_by('-created_at').first()
        data = {
            "info": MentorSerializer(user.mentor).data,
            "name": user.name,
            "mentoringRecord": mentoringRecord,
            # "myMentoring": myMentoring,
            # "myReview": MyReviewSerializer(latest_review).data,
            # "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
        if myMentoring:
            data["myMentoring"] = myMentoring
        else:
            data["myMentoring"] = []
        if latest_review:
            data["myReview"] = MyReviewSerializer(latest_review).data
        else:
            data["myReview"] = []
        if myLogs:
            data["myLogs"] = MyLogSerializer(myLogs, many=True).data
        else:
            data["myLogs"] = []
    
    # 멘티 정보 추가
    else:
        for code, name in Interest.INTEREST_CHOICES:
            mentoringRecord.append({
                'interest': name,
                'count': chatCountDict.get(code, 0)
            })

        latest_concern = Concern.objects.filter(author=user.mentee).order_by('-created_at').first()
        data = {
            "info": MenteeSerializer(user.mentee).data,
            "name": user.name,
            # "concerns": MyConcernSerializer(latest_concern).data,
            "mentoringRecord": mentoringRecord,
            # "myMentoring": myMentoring,
            # "myLogs" : MyLogSerializer(myLogs, many=True).data
        }
        if latest_concern:
            data["concern"] = MyConcernSerializer(latest_concern).data
        else:
            data["concern"] = []
        if myMentoring:
            data["myMentoring"] = myMentoring
        else:
            data["myMentoring"] = []
        if myLogs:
            data["myLogs"] = MyLogSerializer(myLogs, many=True).data
        else:
            data["myLogs"] = []

    return Response(data)

@api_view(['GET'])
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # 멘토링 내역
    if user.is_mentor:
        chatrooms = Chatroom.objects.filter(mentor=user.mentor)
    else:
        chatrooms = Chatroom.objects.filter(mentee=user.mentee)

    chatCount = chatrooms.values('interests__name').annotate(count=Count('id'))

    chatCountDict = {record['interests__name']: record['count'] for record in chatCount}

    mentoringRecord = []    
    # 멘토 프로필
    if user.is_mentor:
        for interest in user.mentor.interests.all():
            mentoringRecord.append({
                'interest': interest.name,
                'count': chatCountDict.get(interest.name, 0)
        })
        myMentoring = MyChatRoomSerializer(chatrooms, many=True).data
        latest_review = Review.objects.filter(mentor=user.mentor).order_by('-created_at').first()

        data = {
            "info": MentorSerializer(user.mentor).data,
            "name": user.name,
            "mentoringRecord": mentoringRecord,
        }

        # 멘토링 내역이 있으면 보여주고 없으면 빈 배열 반환
        if myMentoring:
            data["myMentoring"] = myMentoring
        else:
            data["myMentoring"] = []

        # 후기 내역 있으면 보여주고 없으면 빈 배열 반환
        if latest_review:
            data["myReview"] = MyReviewSerializer(latest_review).data
        else:
            data["myReview"] = []

    # 멘티 프로필
    else:
        for code, name in Interest.INTEREST_CHOICES:
            mentoringRecord.append({
                'interest': name,
                'count': chatCountDict.get(code, 0)
            })
        myMentoring = MyChatRoomSerializer(chatrooms, many=True).data
        latest_concern = Concern.objects.filter(author=user.mentee).order_by('-created_at').first()
        data = {
            "name": user.name,
            "concern": MyConcernSerializer(latest_concern).data,
            "mentoringRecord": mentoringRecord,
        }
        if myMentoring:
            data["myMentoring"] = myMentoring
        else:
            data["myMentoring"] = []

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
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        if user.is_mentor:
            reviews = Review.objects.filter(mentor=user.mentor)
        else:
            reviews = Review.objects.filter(mentee=user.mentee)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='my-mentoring')
    def my_mentoring(self, request):
        user = request.user

        if user.is_mentor:
            return Response({"error" : "멘토는 후기를 작성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            my_mentoring = Chatroom.objects.filter(mentee=user.mentee, mentor_response=True)
            return Response({
                "my_mentoring" : ChatRoomSerializer(my_mentoring, many=True).data
            })
    
    def create(self, request):
        user = request.user
        data = request.data

        if user.is_mentor:
            return Response({"error":"멘토는 후기를 작성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            chatroom = get_object_or_404(Chatroom, pk=data.get('chatroomId'))
            mentor = chatroom.mentor
            score = data.get("score")

            review = Review.objects.create(
                mentee = user.mentee,
                mentor = mentor,
                chatroom = chatroom,
                content = data.get("content"),
                score = score
            )

            # 멘토의 등대지수 업데이트
            mentor.update_rating(score)
            return Response({"리뷰 작성을 완료하였습니다."})



