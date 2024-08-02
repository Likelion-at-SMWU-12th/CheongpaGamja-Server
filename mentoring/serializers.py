from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *
from users.serializers import *

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

    class Meta:
        model = Concern
        fields = ['id', 'author', 'interests', 'content', 'comments']

