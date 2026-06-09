from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models
from .models import User, UserProfile


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Custom serializer for token obtain - accepts username or email"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Use our custom authentication backend - accepts username or email
            from django.contrib.auth import authenticate
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                raise serializers.ValidationError("Foydalanuvchi nomi, email yoki parol noto'g'ri")

            if not user.is_active:
                raise serializers.ValidationError("Hisob faol emas")

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Foydalanuvchi nomi/email va parol kiritish shart")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def validate(self, attrs):
        errors = {}
        
        # Email uniqueness check
        if User.objects.filter(email=attrs['email']).exists():
            errors['email'] = "Bu email allaqachon ro'yxatdan o'tgan"
        
        # Username uniqueness check
        if User.objects.filter(username=attrs['username']).exists():
            errors['username'] = "Bu username allaqachon band"
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # UserProfile signal orqali avtomatik yaratiladi
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('user_info', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'role': obj.user.role,
            'email_verified': obj.email_verified,
            'date_joined': obj.user.date_joined,
            'last_login': obj.user.last_login,
            'target_band_score': obj.target_band_score,
            'target_date': str(obj.target_date) if obj.target_date else None,
            'current_band_score': obj.current_band_score,
            'daily_study_hours': obj.daily_study_hours,
            'exam_type': obj.exam_type,
            'listening_score': obj.listening_score,
            'reading_score': obj.reading_score,
            'writing_score': obj.writing_score,
            'speaking_score': obj.speaking_score,
            'weak_skills': obj.weak_skills,
            'strong_skills': obj.strong_skills,
            'onboarding_completed': obj.onboarding_completed,
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    target_band_score = serializers.FloatField(required=False, allow_null=True)
    target_date = serializers.DateField(required=False, allow_null=True)
    current_band_score = serializers.FloatField(required=False, allow_null=True)
    daily_study_hours = serializers.FloatField(required=False, allow_null=True)
    exam_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    weak_skills = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    strong_skills = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    onboarding_completed = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'target_band_score', 'target_date',
                  'current_band_score', 'daily_study_hours', 'exam_type',
                  'weak_skills', 'strong_skills', 'onboarding_completed')

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        # Profile fields
        profile_fields = [
            'target_band_score', 'target_date', 'current_band_score',
            'daily_study_hours', 'exam_type', 'weak_skills', 'strong_skills',
            'onboarding_completed'
        ]

        profile_data = {}
        for field in profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update profile fields
        profile = instance.userprofile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)

        instance.save()
        profile.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Yangi parollar mos emas")
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Joriy parol noto'g'ri")
        return value


class GoogleAuthSerializer(serializers.Serializer):
    """Clean Google OAuth serializer"""
    id_token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Google ID token from frontend"
    )

    def validate_id_token(self, value):
        """Validate id_token format"""
        if not value or len(value) < 100:
            raise serializers.ValidationError("Invalid token format")
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email bilan foydalanuvchi topilmadi")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Parollar mos emas")
        return attrs

