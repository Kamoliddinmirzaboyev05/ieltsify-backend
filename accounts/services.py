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
    def create_user_with_profile(username, email, password, first_name, last_name, role='user'):
        """Foydalanuvchi va profil yaratish"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # User yaratish
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                
                # UserProfile signal orqali avtomatik yaratiladi
                
                logger.info(f"User created successfully: {user.email}")
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
        # refresh['has_unlimited_access'] = user.userprofile.has_unlimited_access()
        
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
                # 'has_unlimited_access': user.userprofile.has_unlimited_access()
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
        try:
            token, uid = UserService.generate_password_reset_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            subject = "IELTSify - Parolni tiklash"
            
            # HTML template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>IELTSify - Parolni tiklash</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #FF9800; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #FF9800; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Parolni tiklash</h1>
                    </div>
                    <div class="content">
                        <p>Assalomu alaykum <strong>{user.first_name} {user.last_name}</strong>,</p>
                        <p>IELTSify platformasida parolingizni tiklash uchun so'rov yubordingiz.</p>
                        <div class="warning">
                            <p><strong>Eslatma:</strong> Ushbu havola <strong>24 soat</strong> ichida amal qiladi.</p>
                        </div>
                        <p>Parolni tiklash uchun quyidagi tugmani bosing:</p>
                        <a href="{reset_url}" class="button">Parolni tiklash</a>
                        <p>Agar tugma ishlamasa, quyidagi havolani nusxalab brauzerga oling:</p>
                        <p><a href="{reset_url}">{reset_url}</a></p>
                        <p><strong>Xavfsizlik eslatma:</strong></p>
                        <ul>
                            <li>Hech qachon parolingizni kimsa bilan ulashmang</li>
                            <li>Parolingizni muntazam ravishda o'zgartirib turishni maslahat beramiz</li>
                            <li>Agar siz parolni tiklashni so'ramagan bo'lsangiz, iltimos, bu emailni e'tiborsiz qoldiring</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 IELTSify. Barcha huquqlar himoyalangan.</p>
                        <p>Agar siz ushbu emailni xato qabul qilgan bo'lsangiz, iltimos, biz bilan bog'laning.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                subject,
                f"Assalomu alaykum {user.first_name}, parolni tiklash uchun havola: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False
            )
            logger.info(f"Password reset email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False






class EmailService:
    """Email xizmatlari uchun professional service klassi"""
    
    @staticmethod
    def send_welcome_email(user):
        """Xush kelibsiz emaili yuborish"""
        try:
            subject = "IELTSify ga xush kelibsiz!"
            
            # HTML template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>IELTSify - Xush kelibsiz</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>IELTSify ga xush kelibsiz!</h1>
                    </div>
                    <div class="content">
                        <p>Assalomu alaykum <strong>{user.first_name} {user.last_name}</strong>,</p>
                        <p>IELTSify platformasiga muvaffaqiyatli ro'yxatdan o'tdingiz. IELTS imtihoniga tayyorgarlik ko'rish uchun eng yaxshi platformada ekansiz!</p>
                        <p>Bizning platformamizda siz:</p>
                        <ul>
                            <li>Interactive mashqlar bilan shug'ullanishingiz mumkin</li>
                            <li>Real IELTS testlarini yechishingiz mumkin</li>
                            <li>Shaxsiy progress trackingdan foydalanishingiz mumkin</li>
                            <li>Professional o'qituvchilardan maslahat olishingiz mumkin</li>
                        </ul>
                        <p>Tizimga kirish uchun quyidagi tugmani bosing:</p>
                        <a href="{settings.FRONTEND_URL}/login" class="button">Tizimga kirish</a>
                        <p>Agar siz ro'yxatdan o'tmagan bo'lsangiz, iltimos, bu emailni e'tiborsiz qoldiring.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 IELTSify. Barcha huquqlar himoyalangan.</p>
                        <p>Agar siz ushbu emailni xato qabul qilgan bo'lsangiz, iltimos, biz bilan bog'laning.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                subject,
                f"Assalomu alaykum {user.first_name}, IELTSify platformasiga xush kelibsiz! Tizimga kirish uchun: {settings.FRONTEND_URL}/login",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False
            )
            logger.info(f"Welcome email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_email(user):
        """Email tasdiqlash xati yuborish"""
        try:
            # Token generatsiya qilish
            token = secrets.token_urlsafe(32)
            user.userprofile.email_verification_token = token
            user.userprofile.save()
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
            subject = "IELTSify - Emailni tasdiqlash"
            
            # HTML template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>IELTSify - Email tasdiqlash</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2196F3; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Emailni tasdiqlash</h1>
                    </div>
                    <div class="content">
                        <p>Assalomu alaykum <strong>{user.first_name} {user.last_name}</strong>,</p>
                        <p>IELTSify platformasida ro'yxatdan o'tish uchun emailingizni tasdiqlashingiz kerak.</p>
                        <div class="warning">
                            <p><strong>Eslatma:</strong> Ushbu havola <strong>{settings.EMAIL_VERIFICATION_CODE_TTL_MINUTES} daqiqa</strong> ichida amal qiladi.</p>
                        </div>
                        <p>Emailni tasdiqlash uchun quyidagi tugmani bosing:</p>
                        <a href="{verification_url}" class="button">Emailni tasdiqlash</a>
                        <p>Agar tugma ishlamasa, quyidagi havolani nusxalab brauzerga oling:</p>
                        <p><a href="{verification_url}">{verification_url}</a></p>
                        <p>Agar siz ro'yxatdan o'tmagan bo'lsangiz, iltimos, bu emailni e'tiborsiz qoldiring.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 IELTSify. Barcha huquqlar himoyalangan.</p>
                        <p>Agar siz ushbu emailni xato qabul qilgan bo'lsangiz, iltimos, biz bilan bog'laning.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                subject,
                f"Assalomu alaykum {user.first_name}, emailingizni tasdiqlash uchun havola: {verification_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False
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
            logger.warning(f"Invalid verification token: {token}")
            return None


class GoogleAuthService:
    """Google autentifikatsiyasi uchun professional service"""
    
    @staticmethod
    def verify_google_token(id_token):
        """Google ID tokenini tekshirish"""
        try:
            # Agar GOOGLE_CLIENT_ID bo'lmasa, mock qaytaramiz
            if not settings.GOOGLE_CLIENT_ID:
                logger.warning("GOOGLE_CLIENT_ID not configured, using mock data")
                return {
                    'email': 'test@example.com',
                    'name': 'Test User',
                    'given_name': 'Test',
                    'family_name': 'User',
                    'sub': '1234567890',
                    'picture': 'https://example.com/photo.jpg'
                }
            
            from google.auth.transport import requests
            from google.oauth2 import id_token
            
            # Google token validation
            idinfo = id_token.verify_oauth2_token(
                id_token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            # Token haqiqiyligini tekshirish
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.warning("Wrong issuer.")
                return None
                
            return idinfo
            
        except Exception as e:
            logger.error(f"Google token verification failed: {str(e)}")
            return None
    
    @staticmethod
    def create_or_update_google_user(user_info):
        """Google foydalanuvchisini yaratish yoki yangilash"""
        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=user_info['email'],
                    defaults={
                        'username': user_info['email'].split('@')[0] + f"_{user_info.get('sub', '')[:8]}",
                        'first_name': user_info.get('given_name', ''),
                        'last_name': user_info.get('family_name', ''),
                        'role': 'user'
                    }
                )
                
                if not created:
                    # Mavjud foydalanuvchini yangilash
                    user.first_name = user_info.get('given_name', user.first_name)
                    user.last_name = user_info.get('family_name', user.last_name)
                    user.save()
                
                # UserProfile ni yaratish yoki olish
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'email_verified': True,  # Google orqali kelgan foydalanuvchi emaili tasdiqlangan
                        'email_verification_token': None
                    }
                )
                
                if not profile_created and not profile.email_verified:
                    profile.email_verified = True
                    profile.email_verification_token = None
                    profile.save()
                
                logger.info(f"Google user {'created' if created else 'updated'}: {user.email}")
                return user, created
                
        except Exception as e:
            logger.error(f"Error creating/updating Google user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_google_user(id_token):
        """Google foydalanuvchisini autentifikatsiya qilish"""
        try:
            # Tokenni tekshirish
            user_info = GoogleAuthService.verify_google_token(id_token)
            if not user_info:
                raise ValueError("Invalid Google token")
            
            # Foydalanuvchini yaratish yoki yangilash
            user, created = GoogleAuthService.create_or_update_google_user(user_info)
            
            # Tokenlar generatsiya qilish
            tokens = UserService.generate_jwt_tokens(user)
            
            return {
                'user': user,
                'tokens': tokens,
                'created': created,
                'email_verified': user.userprofile.email_verified
            }
            
        except Exception as e:
            logger.error(f"Google authentication failed: {str(e)}")
            raise
