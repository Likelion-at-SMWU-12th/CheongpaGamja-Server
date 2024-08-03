from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *
from users.serializers import *
from chatting.models import *
from django.db.models import Count

class ConcernSerializer(serializers.ModelSerializer):
    author = MenteeSerializer(read_only=True)
    interests_ids = InterestSerializer(many=True, read_only=True)

    interests = serializers.ListField(
        child=serializers.SlugRelatedField(
            queryset=Interest.objects.all(),
            slug_field='name'
        ),
        allow_empty=False,  # Ensures at least one interest is required
        write_only=True
    )

    class Meta:
        model = Concern
        fields = ['author','interests_ids', 'interests', 'content']
    
        def create(self, validated_data):
            author = self.context['request'].user.mentee
            concerns = Concern.objects.create(author=author, content=validated_data['content'])
            interests_data = validated_data.pop('interests')
        
            for interest_name in interests_data:
                interest = Interest.objects.get(name=interest_name)
                ConcernInterest.objects.create(concern=concerns, interest=interest)
            
            return concerns

class CommentSerializer(serializers.ModelSerializer):
    # author = MentorInterest()
    # author = MentorSerializer(read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['author', 'content']
    
    def get_author(self, obj):
        return obj.author.user.id

class ConcernViewSerializer(serializers.ModelSerializer):
    author = MenteeSerializer()
    interests = InterestSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    mentee_name = serializers.CharField(source='author.user.name', read_only=True)

    class Meta:
        model = Concern
        fields = ['id', 'author','mentee_name', 'interests', 'content', 'comments']
        
class MentorViewSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='user.name', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    mentoring_record = serializers.SerializerMethodField()
    mentor_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Mentor
        fields = ['user', 'mentor_id', 'mentor_name', 'is_subscribed', 'mentoring_record', 'rating']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        return obj.like_mentees.filter(id=user.mentee.id).exists()

    def get_mentoring_record(self, obj):
        user = obj.user

        if user.is_mentor:
            chatrooms = Chatroom.objects.filter(mentor=user.mentor)
        else:
            chatrooms = Chatroom.objects.filter(mentee=user.mentee)

        chatCount = chatrooms.values('interests__name').annotate(count=Count('id'))
        chatCountDict = {record['interests__name']: record['count'] for record in chatCount}

        mentoringRecord = []
        if user.is_mentor:
            for interest in user.mentor.interests.all():
                mentoringRecord.append({
                    'interest': interest.name,
                    'count': chatCountDict.get(interest.name, 0)
                })
        
        return mentoringRecord
    