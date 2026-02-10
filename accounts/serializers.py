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
        # Email uniqueness check
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan")
        
        # Username uniqueness check
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Bu username allaqachon band")
        
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
        fields = ('user_info', 'email_verified', 'created_at')
        read_only_fields = ('created_at',)

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'role': obj.user.role,
            'is_vip': obj.is_vip,
            'vip_expires_at': obj.vip_expires_at,
            'email_verified': obj.email_verified,
            'date_joined': obj.user.date_joined,
            'last_login': obj.user.last_login
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'current_password', 'new_password')

    def validate(self, attrs):
        if 'new_password' in attrs and 'current_password' not in attrs:
            raise serializers.ValidationError("Yangi parol uchun joriy parolni kiriting")

        if 'current_password' in attrs:
            if not self.instance.check_password(attrs['current_password']):
                raise serializers.ValidationError("Joriy parol noto'g'ri")

        return attrs

    def update(self, instance, validated_data):
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if new_password:
            instance.set_password(new_password)

        instance.save()
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
    id_token = serializers.CharField(required=True)

    def validate_id_token(self, value):
        # Google token validation logic
        # Bu yerda Google API orqali tokenni tekshirish kerak
        # Hozircha placeholder
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
