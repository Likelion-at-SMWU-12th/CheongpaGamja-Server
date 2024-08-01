from users.models import *
from users.serializers import *
from mentoring.models import *
from mentoring.serializers import *
from chatting.models import *
from chatting.serializers import *
from .models import *

# 마이 페이지 멘토링(채팅) 내역
class MyChatRoomSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True)
    mentee_name = serializers.CharField(source='mentee.user.name', read_only=True)

    class Meta:
        model = Chatroom
        fields = ['id','mentee_name','interests', 'title']

# 마이 페이지 고민 내역
class MyConcernSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Concern
        fields = ['id', 'content', 'comments']

# 멘토링 일지
class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

# 멘토링 일지(마이페이지 뷰)
class MyLogSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = ['id', 'title', 'created_at']
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

# 멘토링 후기
class ReviewSerializer(serializers.ModelSerializer):
    chatroom = ChatRoomSerializer(read_only=True)
    mentor_name = serializers.CharField(source='mentor.user.name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.user.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'mentor', 'mentor_name', 'mentee', 'mentee_name', 'content', 'score', 'chatroom']

# 마이페이지(멘토) 후기 내역
class MyReviewSerializer(serializers.ModelSerializer):
    chatroom_interests = serializers.SerializerMethodField()
    mentor_name = serializers.CharField(source='mentor.user.name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.user.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'mentor', 'mentor_name', 'mentee', 'mentee_name', 'content', 'score', 'chatroom_interests']

    def get_chatroom_interests(self, obj):
        chatroom = obj.chatroom
        
        if chatroom:
            interests = chatroom.interests.all()
            return [{'name': interest.name} for interest in interests]  # Adjust based on your Interest model
        return []