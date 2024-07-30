from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *
from users.serializers import *

# User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'name']

# class InterestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Interest
#         fields = ['name']

# class MentorSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     interests = InterestSerializer(many=True)

#     class Meta:
#         model = Mentor
#         fields = ['id', 'user', 'interests', 'rating']

# class MenteeSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     # interests = InterestSerializer(many=True)
#     # 멘티가 관심설정한 멘토 목록

#     class Meta:
#         model = Mentee
#         fields = ['user', 'interests']

class ConcernSerializer(serializers.ModelSerializer):
    author = MenteeSerializer(read_only=True)
    interests_ids = InterestSerializer(many=True, read_only=True)

    interests = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all()),
        allow_empty=False,  # Ensures at least one interest is required
        write_only=True
    )

    class Meta:
        model = Concern
        fields = ['author','interests_ids', 'interests', 'content']
    
        def create(self, validated_data):
            author = self.context['request'].user.mentee
            concerns = Concern.objects.create(author=author, content=validated_data['content'])
            interests = validated_data.get('interests', [])
        
            for interest in interests:
                ConcernInterest.objects.create(concern=concerns, interest=interest)
            
            return concerns

class CommentSerializer(serializers.ModelSerializer):
    author = MentorInterest()
    
    class Meta:
        model = Comment
        fields = ['author', 'content']

class ConcernViewSerializer(serializers.ModelSerializer):
    author = MenteeSerializer()
    interests = InterestSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Concern
        fields = ['author', 'interests', 'content', 'comments']

