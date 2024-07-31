from rest_framework import serializers
from .models import *
from mentoring.serializers import *
from users.serializers import InterestSerializer

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