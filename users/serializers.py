# serializers.py

from rest_framework import serializers
from .models import User, Mentor, Mentee, Interest, MentorInterest

class InterestSerializer(serializers.ModelSerializer):
  class Meta:
    model = Interest
    fields = ['name']

class MentorSerializer(serializers.ModelSerializer):
  # Write-only field to receive interests as choice names
  interests = serializers.ListField(
    child=serializers.ChoiceField(choices=[choice[0] for choice in Interest.INTEREST_CHOICES]),  # 선택 항목의 키 값만 사용
    write_only=True
  )

  # Read-only field to display interests
  interests_display = InterestSerializer(source='interests', many=True, read_only=True)

  class Meta:
    model = Mentor
    fields = [
      'interests',
      'interests_display',
      'rating',
      'total_ratings'
    ]

  def validate_interests(self, value):
    if len(value) > 3:
      raise serializers.ValidationError("멘토는 3개 이하의 관심사를 선택할 수 있습니다.")
    # Interest가 유효한지 검사
    for interest_name in value:
      if not Interest.objects.filter(name=interest_name).exists():
        raise serializers.ValidationError(f"관심사 '{interest_name}'가 유효하지 않습니다.")
    return value

class MenteeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Mentee
    fields = []

class UserSerializer(serializers.ModelSerializer):
  mentor_profile = MentorSerializer(required=False)
  mentee_profile = MenteeSerializer(required=False)

  class Meta:
    model = User
    fields = [
      'id', 'username', 'email', 'password', 'is_mentor', 'name',
      'birth_date', 'profile_pic', 'agreed_to_terms',
      'mentor_profile', 'mentee_profile'
    ]
    extra_kwargs = {
      'password': {'write_only': True},
      'is_mentor': {'read_only': True},
      'agreed_to_terms': {'read_only': True}
    }

  def create(self, validated_data):
    # nested profile data 가져오기
    mentor_data = validated_data.pop('mentor_profile', None)
    mentee_data = validated_data.pop('mentee_profile', None)

    # hashed password 가지고 유저 생성
    user = User.objects.create_user(**validated_data)

    # Mentor 생성
    if user.is_mentor and mentor_data:
      interests_data = mentor_data.pop('interests', [])
      mentor = Mentor.objects.create(user=user, **mentor_data)
      # MentorInterest를 통해 interest 넣기
      for interest_name in interests_data:
        interest = Interest.objects.get(name=interest_name)
        MentorInterest.objects.create(mentor=mentor, interest=interest)

    # Mentee 생성
    elif not user.is_mentor and mentee_data:
      # 멘티는 카테고리를 설정하지 않는다는 새로운 설정!
      Mentee.objects.create(user=user, **mentee_data)

    return user

  def update(self, instance, validated_data):
    mentor_data = validated_data.pop('mentor_profile', None)
    mentee_data = validated_data.pop('mentee_profile', None)

    for attr, value in validated_data.items():
      setattr(instance, attr, value)
    instance.save()
    
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
    return instance
