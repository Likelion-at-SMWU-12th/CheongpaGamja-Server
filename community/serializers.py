# community/serializers.py
from rest_framework import serializers
from .models import Column
from users.models import User, Interest, Mentor
from users.serializers import InterestSerializer, UserSerializer, MentorSerializer

class UserProfileSerializer(serializers.ModelSerializer):
  is_mentor = serializers.BooleanField()
  mentor_profile = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ['id', 'username', 'name', 'is_mentor', 'mentor_profile']

  def get_mentor_profile(self, obj):
    if obj.is_mentor:
      mentor = Mentor.objects.get(user=obj)
      return {
        'rating': mentor.rating,
        'interests': [interest.name for interest in mentor.interests.all()]
      }
    return None

class ColumnSerializer(serializers.ModelSerializer):
  author = UserSerializer(read_only=True)
  categories = InterestSerializer(many=True, read_only=True)
  likes_count = serializers.SerializerMethodField()
  scraps_count = serializers.SerializerMethodField()
  is_liked = serializers.SerializerMethodField()
  is_scraped = serializers.SerializerMethodField()

  class Meta:
    model = Column
    fields = ['id', 'title', 'author', 'published_date', 'content', 'image', 'categories', 'likes_count', 'scraps_count', 'is_liked', 'is_scraped']

  def get_likes_count(self, obj):
    return obj.likes.count()

  def get_scraps_count(self, obj):
    return obj.scraps.count()

  def get_is_liked(self, obj):
    request = self.context.get('request')
    if request and request.user.is_authenticated:
      return obj.likes.filter(id=request.user.id).exists()
    return False

  def get_is_scraped(self, obj):
    request = self.context.get('request')
    print(f"Request: {request}")  # 디버그 출력
    if request and request.user.is_authenticated:
      is_scraped = obj.scraps.filter(id=request.user.id).exists()
      print(f"User: {request.user}, Is scraped: {is_scraped}")  # 디버그 출력
      return is_scraped
    return False

class ColumnCreateSerializer(serializers.ModelSerializer):
  categories = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)

  class Meta:
    model = Column
    fields = ['title', 'content', 'image', 'categories']

  def create(self, validated_data):
    categories = validated_data.pop('categories')
    column = Column.objects.create(**validated_data)
    column.categories.set(categories)
    return column
