from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.generics import RetrieveUpdateAPIView

from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi

from .serializers import (

    UserRegistrationSerializer, UserProfileSerializer,

    UserUpdateSerializer, ChangePasswordSerializer,

    GoogleAuthSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, CustomTokenObtainPairSerializer

)

from .services import UserService, EmailService, GoogleAuthService

User = get_user_model()


class CustomTokenObtainPairView(APIView):
    """Custom token obtain view - accepts username or email"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Username yoki email orqali tizimga kirish",

        request_body=openapi.Schema(

            type=openapi.TYPE_OBJECT,

            required=['username', 'password'],

            properties={

                'username': openapi.Schema(

                    type=openapi.TYPE_STRING,

                    description='Username yoki email'

                ),

                'password': openapi.Schema(

                    type=openapi.TYPE_STRING,

                    description='Parol'

                )

            }

        ),

        responses={200: openapi.Response(

            description="Muvaffaqiyatli tizimga kirish",

            schema=openapi.Schema(

                type=openapi.TYPE_OBJECT,

                properties={

                    'access': openapi.Schema(type=openapi.TYPE_STRING),

                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),

                    'role': openapi.Schema(type=openapi.TYPE_STRING),

                }

            )

        )}

    )
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Tokenlar generatsiya qilish

            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)

            return Response({

                'access': str(refresh.access_token),

                'refresh': str(refresh),

                'role': str(user.role),

            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationView(APIView):
    """Foydalanuvchi ro'yxatdan o'tishi"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Foydalanuvchini ro'yxatdan o'tkazish",

        request_body=openapi.Schema(

            type=openapi.TYPE_OBJECT,

            required=['username', 'email', 'first_name', 'last_name', 'password'],

            properties={

                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),

                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email'),

                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Ism'),

                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Familiya'),

                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Parol'),

            }

        ),

        responses={201: openapi.Response(

            description="Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",

            schema=openapi.Schema(

                type=openapi.TYPE_OBJECT,

                properties={

                    'message': openapi.Schema(type=openapi.TYPE_STRING),

                    'user': openapi.Schema(

                        type=openapi.TYPE_OBJECT,

                        properties={

                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),

                            'username': openapi.Schema(type=openapi.TYPE_STRING),

                            'email': openapi.Schema(type=openapi.TYPE_STRING),

                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),

                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),

                            'role': openapi.Schema(type=openapi.TYPE_STRING)

                        }

                    ),

                    'tokens': openapi.Schema(

                        type=openapi.TYPE_OBJECT,

                        properties={

                            'access': openapi.Schema(type=openapi.TYPE_STRING),

                            'refresh': openapi.Schema(type=openapi.TYPE_STRING)

                        }

                    )

                }

            )

        )}

    )
    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():

            try:

                user = UserService.create_user_with_profile(serializer.validated_data)

                # Xush kelibsiz email yuborish

                # EmailService.send_welcome_email(user)
                #
                # EmailService.send_verification_email(user)

                # Tokenlar generatsiya qilish

                tokens = UserService.generate_jwt_tokens(user)

                return Response({

                    'message': 'Foydalanuvchi muvaffaqiyatli ro\'yxatdan o\'tdi',

                    'tokens': tokens

                }, status=status.HTTP_201_CREATED)



            except Exception as e:

                return Response({

                    'error': 'Ro\'yxatdan o\'tishda xatolik',

                    'detail': str(e)

                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    """Foydalanuvchi profilini ko'rish va yangilash"""

    serializer_class = UserProfileSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):

        return self.request.user.userprofile

    def get_serializer_class(self):

        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer

        return UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):

        profile = self.get_object()

        serializer = self.get_serializer(profile)

        return Response({
            'success': True,
            'data': {
                **serializer.data,
                'is_active': profile.user.is_active,
                'is_staff': profile.user.is_staff,
                'is_superuser': profile.user.is_superuser
            }
        })

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)

        instance = self.get_object()

        if request.method in ['PUT', 'PATCH']:

            serializer = UserUpdateSerializer(

                instance.user,

                data=request.data,

                partial=partial

            )

            serializer.is_valid(raise_exception=True)

            try:

                user = UserService.update_user_profile(

                    instance.user,

                    serializer.validated_data

                )

                # Yangi tokenlar generatsiya qilish

                tokens = UserService.generate_jwt_tokens(user)

                return Response({

                    'message': 'Profil muvaffaqiyatli yangilandi',

                    'user': tokens['user'],

                }, status=status.HTTP_200_OK)



            except Exception as e:

                return Response({

                    'error': 'Profilni yangilashda xatolik',

                    'detail': str(e)

                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance)

        return Response({

            'success': True,

            'data': serializer.data

        })


class ChangePasswordView(APIView):
    """Parolni o'zgartirish"""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(

        operation_description="Foydalanuvchi parolini o'zgartirish",

        request_body=openapi.Schema(

            type=openapi.TYPE_OBJECT,

            required=['current_password', 'new_password', 'new_password_confirm'],

            properties={

                'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='Joriy parol'),

                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Yangi parol'),

                'new_password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Yangi parolni tasdiqlash')

            }

        ),

        responses={200: openapi.Response(

            description="Parol muvaffaqiyatli o'zgartirildi"

        )}

    )
    def post(self, request):

        serializer = ChangePasswordSerializer(

            data=request.data,

            context={'request': request}

        )

        if serializer.is_valid():

            try:

                UserService.change_password(

                    request.user,

                    serializer.validated_data['current_password'],

                    serializer.validated_data['new_password']

                )

                return Response({

                    'message': 'Parol muvaffaqiyatli o\'zgartirildi'

                }, status=status.HTTP_200_OK)



            except ValueError as e:

                return Response({

                    'error': str(e)

                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthView(APIView):
    """Google autentifikatsiyasi"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Google orqali autentifikatsiya",

        request_body=GoogleAuthSerializer,

        responses={200: UserProfileSerializer}

    )
    def post(self, request):

        serializer = GoogleAuthSerializer(data=request.data)

        if serializer.is_valid():

            id_token = serializer.validated_data['id_token']

            # Google tokenini tekshirish

            user_info = GoogleAuthService.verify_google_token(id_token)

            if not user_info:
                return Response({

                    'error': 'Google tokeni noto\'g\'ri'

                }, status=status.HTTP_400_BAD_REQUEST)

            try:

                # Foydalanuvchini yaratish yoki yangilash

                user, created = GoogleAuthService.create_or_update_google_user(user_info)

                # Tokenlar generatsiya qilish

                tokens = UserService.generate_jwt_tokens(user)

                message = 'Google orqali muvaffaqiyatli ro\'yxatdan o\'tdingiz' if created else 'Google orqali muvaffaqiyatli tizimga kirdingiz'

                return Response({

                    'message': message,

                    'user': tokens['user'],

                    'tokens': tokens

                }, status=status.HTTP_200_OK)



            except Exception as e:

                return Response({

                    'error': 'Google autentifikatsiyasida xatolik',

                    'detail': str(e)

                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Parolni tiklash"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Parolni tiklash uchun email yuborish",

        request_body=PasswordResetSerializer,

        responses={200: openapi.Response(description="Email yuborildi")}

    )
    def post(self, request):

        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data['email']

            try:

                user = User.objects.get(email=email)

                success = UserService.send_password_reset_email(user)

                if success:

                    return Response({

                        'message': 'Parolni tiklash linki emailingizga yuborildi'

                    }, status=status.HTTP_200_OK)

                else:

                    return Response({

                        'error': 'Email yuborishda xatolik'

                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



            except User.DoesNotExist:

                # Xavfsizlik uchun xatolikni ko'rsatmaymiz

                return Response({

                    'message': 'Agar bu email mavjud bo\'lsa, parolni tiklash linki yuboriladi'

                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Parolni tiklashni tasdiqlash"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Parolni tiklashni tasdiqlash",

        request_body=PasswordResetConfirmSerializer,

        responses={200: openapi.Response(description="Parol muvaffaqiyatli o'zgartirildi")}

    )
    def post(self, request):

        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():

            uid = serializer.validated_data['token'].split(':')[0]

            token = serializer.validated_data['token'].split(':')[1]

            new_password = serializer.validated_data['new_password']

            user = UserService.verify_password_reset_token(uid, token)

            if not user:
                return Response({

                    'error': 'Token noto\'g\'ri yoki muddati o\'tgan'

                }, status=status.HTTP_400_BAD_REQUEST)

            try:

                user.set_password(new_password)

                user.save()

                return Response({

                    'message': 'Parol muvaffaqiyatli o\'zgartirildi'

                }, status=status.HTTP_200_OK)



            except Exception as e:

                return Response({

                    'error': 'Parolni o\'zgartirishda xatolik',

                    'detail': str(e)

                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """Emailni tasdiqlash"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(

        operation_description="Emailni tasdiqlash token orqali",

        manual_parameters=[

            openapi.Parameter(

                'token',

                openapi.IN_PATH,

                description="Tasdiqlash tokeni",

                type=openapi.TYPE_STRING,

                required=True

            )

        ],

        responses={200: openapi.Response(description="Email muvaffaqiyatli tasdiqlandi")}

    )
    def get(self, request, token):
        user = EmailService.verify_email(token)

        if not user:
            return Response({

                'error': 'Token noto\'g\'ri yoki muddati o\'tgan'

            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({

            'message': 'Email muvaffaqiyatli tasdiqlandi'

        }, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    """Tasdiqlash emailini qayta yuborish"""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(

        operation_description="Tasdiqlash emailini qayta yuborish",

        responses={200: openapi.Response(description="Tasdiqlash emaili qayta yuborildi")}

    )
    def post(self, request):

        if request.user.userprofile.email_verified:
            return Response({

                'error': 'Email allaqachon tasdiqlangan'

            }, status=status.HTTP_400_BAD_REQUEST)

        success = EmailService.send_verification_email(request.user)

        if success:

            return Response({

                'message': 'Tasdiqlash emaili qayta yuborildi'

            }, status=status.HTTP_200_OK)

        else:

            return Response({

                'error': 'Email yuborishda xatolik'

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
