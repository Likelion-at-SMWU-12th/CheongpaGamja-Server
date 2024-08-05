# serializers.py
from rest_framework import serializers
from .models import User, Mentor, Mentee, Interest, MentorInterest

class InterestSerializer(serializers.ModelSerializer):
  class Meta:
    model = Interest
    fields = ['name']

class MentorSerializer(serializers.ModelSerializer):
  interests = serializers.MultipleChoiceField(choices=Interest.INTEREST_CHOICES, write_only=True)
  interests_display = serializers.SerializerMethodField()
  mentor_name = serializers.CharField(source='user.name', read_only=True)

  class Meta:
    model = Mentor
    fields = [
      'id', # read-only로!
      'user', # read-only로!
      'mentor_name',
      'interests',
      'interests_display',
      'rating',
      'total_ratings'
    ]
    read_only_fields = ['id', 'user']
  def get_interests_display(self, obj):
    return [{'name': interest.name} for interest in obj.interests.all()]

  def validate_interests(self, value):
    if len(value) > 3:
      raise serializers.ValidationError("멘토는 3개 이하의 관심사를 선택할 수 있습니다.")
    # Interest가 유효한지 검사
    for interest_name in value:
      if not Interest.objects.filter(name=interest_name).exists():
        raise serializers.ValidationError(f"관심사 '{interest_name}'가 유효하지 않습니다.")
    return value

class MenteeSerializer(serializers.ModelSerializer):
  # user = UserSerializer()

  class Meta:
    model = Mentee
    fields = [
      'id',
      'user'
    ]
    read_only_fields = ['id', 'user']

class UserSerializer(serializers.ModelSerializer):
  mentor_profile = MentorSerializer(source='mentor', required=False) 
  mentee_profile = MenteeSerializer(source='mentee', required=False)
  interests = serializers.MultipleChoiceField(choices=Interest.INTEREST_CHOICES, write_only=True, required=False)


  class Meta:
    model = User
    fields = [
      'id', 'username', 'email', 'password', 'is_mentor', 'name',
      'birth_date', 'profile_pic', 'agreed_to_terms',
      'mentor_profile', 'mentee_profile', 'interests'
    ]
    extra_kwargs = {
      'password': {'write_only': True},
    }

  def create(self, validated_data):

    # # hashed password 가지고 유저 생성
    # user = User.objects.create_user(**validated_data)
    mentor_data = validated_data.pop('mentor_profile', None)
    mentee_data = validated_data.pop('mentee_profile', None)

    password = validated_data.pop('password')
    user = User(**validated_data)
    user.set_password(password)
    user.save()

    # Mentor 생성
    if user.is_mentor and mentor_data:
      interests_data = mentor_data.pop('interests', [])
      mentor = Mentor.objects.create(user=user, **mentor_data)
      # MentorInterest를 통해 interest 넣기
      for interest_name in interests_data:
        interest = Interest.objects.get(name=interest_name)
        mentor.interests.add(interest)
        # MentorInterest.objects.create(mentor=mentor, interest=interest)

    # Mentee 생성
    elif not user.is_mentor:
      Mentee.objects.create(user=user, **(mentee_data or {}))
    return user

  def update(self, instance, validated_data):
    mentor_data = validated_data.pop('mentor_profile', None)
    mentee_data = validated_data.pop('mentee_profile', None)
    interests_data = validated_data.pop('interests', None)
    
    instance = super().update(instance, validated_data)

    # for attr, value in validated_data.items():
    #   setattr(instance, attr, value)
    # instance.save()
    
    # Update mentor profile
    if instance.is_mentor and mentor_data:
      mentor_serializer = MentorSerializer(instance.mentor_profile, data=mentor_data, partial=True)
      if mentor_serializer.is_valid():
        mentor_serializer.save()
      else:
        print(f"Mentor serializer errors: {mentor_serializer.errors}")

    # Update mentee profile 
    elif not instance.is_mentor and mentee_data:
      mentee_serializer = MenteeSerializer(instance.mentee_profile, data=mentee_data, partial=True)
      if mentee_serializer.is_valid():
        mentee_serializer.save()
      else:
        print(f"Mentee serializer errors: {mentee_serializer.errors}")

    # 관심사 업데이트
    if interests_data is not None and instance.is_mentor:
      mentor = instance.mentor
      mentor.interests.clear()
      for interest_name in interests_data:
        interest, _ = Interest.objects.get_or_create(name=interest_name)
        mentor.interests.add(interest)
    return instance