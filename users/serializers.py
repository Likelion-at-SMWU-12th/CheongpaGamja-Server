# serializers.py
from rest_framework import serializers
from .models import User, Mentor, Mentee, Interest, MentorInterest

class InterestSerializer(serializers.ModelSerializer):
  class Meta:
    model = Interest
    fields = ['name']

class MentorSerializer(serializers.ModelSerializer):
  # Write-only field to receive interests as choice names
  # interests = serializers.ListField(
  #   child=serializers.ChoiceField(choices=[choice[0] for choice in Interest.INTEREST_CHOICES]),  # 선택 항목의 키 값만 사용
  #   write_only=True
  # )
  interests = serializers.MultipleChoiceField(choices=Interest.INTEREST_CHOICES, write_only=True)
  interests_display = serializers.SerializerMethodField()
  mentor_name = serializers.CharField(source='user.name', read_only=True)
  # Read-only field to display interests
  #interests_display = InterestSerializer(source='interests', many=True, read_only=True)

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
  mentor_profile = MentorSerializer(source='mentor', required=False) #근데 리드온리로 하면 나중에 수정 못하는거 아냐?
  mentee_profile = MenteeSerializer(source='mentee', required=False)

  class Meta:
    model = User
    fields = [
      'id', 'username', 'email', 'password', 'is_mentor', 'name',
      'birth_date', 'profile_pic', 'agreed_to_terms',
      'mentor_profile', 'mentee_profile'
    ]
    extra_kwargs = {
      'password': {'write_only': True},
      # 유저 정보 수정 과정에서 아래는 수정불가하게 하고 싶어서 쓴건데 이때문에 회원가입 절차에서 defualt값인 False로만 저장되더라...
      # 'is_mentor': {'read_only': True},
      # 'agreed_to_terms': {'read_only': True}
    }

  def create(self, validated_data):
    # # nested profile data 가져오기
    # mentor_data = validated_data.pop('mentor_profile', None)
    # mentee_data = validated_data.pop('mentee_profile', None)

    # # hashed password 가지고 유저 생성
    # user = User.objects.create_user(**validated_data)
    mentor_data = validated_data.pop('mentor', None)
    mentee_data = validated_data.pop('mentee', None)

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
      # if mentee_data is None:
      #   mentee_data = {}
      # 멘티는 카테고리를 설정하지 않는다는 새로운 설정!
      # Mentee.objects.create(user=user, **mentee_data)
      Mentee.objects.create(user=user, **(mentee_data or {}))
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