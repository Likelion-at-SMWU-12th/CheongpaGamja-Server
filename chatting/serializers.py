from rest_framework import serializers
from .models import *
from mentoring.serializers import *
from users.serializers import InterestSerializer
from .utils import time_difference

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
    mentor_id = serializers.IntegerField(source='mentor.user.id', read_only=True)
    mentee_id = serializers.IntegerField(source='mentee.user.id', read_only=True)
    chats = ChatSerializer(many=True, read_only=True, source='chat_set')
    last_chat = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom
        fields = ['id', 'interests', 'title', 'mentor_response', 'mentor','mentor_name', 'mentor_id', 'last_chat', 'mentee', 'mentee_name', 'mentee_id', 'chats']

    def get_last_chat(self, obj):
        last_chat = obj.chat_set.order_by('-created_at').first()
        if last_chat:
            return time_difference(last_chat.created_at)
        return None