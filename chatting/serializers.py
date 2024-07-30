from rest_framework import serializers
from .models import *
from mentoring.serializers import *
from users.serializers import *

class ChatSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields =['id', 'message', 'is_mentee', 'created_at', 'room']
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

class ChatRoomSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True)
    mentor_name = serializers.CharField(source='mentor.user.name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.user.name', read_only=True)
    chats = ChatSerializer(many=True, read_only=True, source='chat_set')

    class Meta:
        model = Chatroom
        fields = ['id', 'interests', 'title', 'mentor', 'mentor_name', 'mentee', 'mentee_name', 'chats']

# 마이 페이지 멘토링(채팅) 내역
class MyChatRoomSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True)
    mentee_name = serializers.CharField(source='mentee.user.name', read_only=True)

    class Meta:
        model = Chatroom
        fields = ['id','mentee_name','interests', 'title']

# 마이 페이지 고민 내역
class MyConcernSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concern
        fields = ['id', 'content']

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