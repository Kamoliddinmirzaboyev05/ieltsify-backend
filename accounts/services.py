import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile
import secrets
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Foydalanuvchilar bilan ishlash uchun service klassi"""
    
    @staticmethod
    def create_user_with_profile(user_data):
        """Foydalanuvchi va profilini yaratish"""
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role='user'
            )
            
            # UserProfile signal orqali avtomatik yaratiladi

            logger.info(f"New user created: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    
    @staticmethod
    def authenticate_user(email, password):
        """Foydalanuvchini autentifikatsiya qilish"""
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def generate_jwt_tokens(user):
        """JWT tokenlar generatsiya qilish"""
        refresh = RefreshToken.for_user(user)
        
        # Custom claims qo'shish
        refresh['role'] = user.role
        refresh['is_vip'] = user.userprofile.is_vip
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_vip': user.userprofile.is_vip
            }
        }
    
    @staticmethod
    def update_user_profile(user, profile_data):
        """Foydalanuvchi profilini yangilash"""
        try:
            for field, value in profile_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
                elif hasattr(user.userprofile, field):
                    setattr(user.userprofile, field, value)
            
            user.save()
            user.userprofile.save()
            
            logger.info(f"Profile updated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise
    
    @staticmethod
    def change_password(user, current_password, new_password):
        """Parolni o'zgartirish"""
        if not user.check_password(current_password):
            raise ValueError("Joriy parol noto'g'ri")
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password changed: {user.email}")
    
    @staticmethod
    def generate_password_reset_token(user):
        """Parolni tiklash uchun token generatsiya qilish"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return token, uid
    
    @staticmethod
    def verify_password_reset_token(uid, token):
        """Parolni tiklash tokenini tekshirish"""
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return user
            return None
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
    
    @staticmethod
    def send_password_reset_email(user):
        """Parolni tiklash emailini yuborish"""
        token, uid = UserService.generate_password_reset_token(user)
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        subject = "IELTSify - Parolni tiklash"
        message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message
            )
            logger.info(f"Password reset email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False






class EmailService:
    """Email xizmatlari uchun service klassi"""
    
    @staticmethod
    def send_welcome_email(user):
        """Xush kelibsiz emaili yuborish"""
        subject = "IELTSify ga xush kelibsiz!"
        message = render_to_string('emails/welcome.html', {
            'user': user,
            'login_url': f"{settings.FRONTEND_URL}/login"
        })
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message
            )
            logger.info(f"Welcome email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_email(user):
        """Email tasdiqlash xati yuborish"""
        token = secrets.token_urlsafe(32)
        user.userprofile.email_verification_token = token
        user.userprofile.save()
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
        
        subject = "IELTSify - Emailni tasdiqlash"
        message = render_to_string('emails/email_verification.html', {
            'user': user,
            'verification_url': verification_url
        })
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message
            )
            logger.info(f"Verification email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def verify_email(token):
        """Emailni tasdiqlash"""
        try:
            profile = UserProfile.objects.get(email_verification_token=token)
            profile.email_verified = True
            profile.email_verification_token = None
            profile.save()
            
            logger.info(f"Email verified: {profile.user.email}")
            return profile.user
            
        except UserProfile.DoesNotExist:
            return None


class GoogleAuthService:
    """Google autentifikatsiyasi uchun service"""
    
    @staticmethod
    def verify_google_token(id_token):
        """Google ID tokenini tekshirish"""
        # Bu yerda Google API orqali tokenni tekshirish kerak
        # Hozircha placeholder implementation
        try:
            # Google token validation logic
            # from google.auth.transport import requests
            # from google.oauth2 import id_token
            
            # idinfo = id_token.verify_oauth2_token(
            #     id_token, 
            #     requests.Request(), 
            #     settings.GOOGLE_CLIENT_ID
            # )
            
            # Placeholder response
            return {
                'email': 'user@gmail.com',
                'name': 'Test User',
                'given_name': 'Test',
                'family_name': 'User',
                'picture': 'https://example.com/photo.jpg'
            }
            
        except Exception as e:
            logger.error(f"Google token verification failed: {str(e)}")
            return None
    
    @staticmethod
    def create_or_update_google_user(user_info):
        """Google foydalanuvchisini yaratish yoki yangilash"""
        try:
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info['email'].split('@')[0],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'role': 'user'
                }
            )
            
            if not created:
                # Mavjud foydalanuvchini yangilash
                user.first_name = user_info.get('given_name', '')
                user.last_name = user_info.get('family_name', '')
                user.save()
            
            logger.info(f"Google user {'created' if created else 'updated'}: {user.email}")
            return user, created
            
        except Exception as e:
            logger.error(f"Error creating/updating Google user: {str(e)}")
            raise
