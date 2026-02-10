from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """
    Faqat admin role ga ega foydalanuvchilarga ruxsat berish
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_admin_role()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_admin_role()


class IsRegularUser(permissions.BasePermission):
    """
    Faqat user role ga ega foydalanuvchilarga ruxsat berish
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_user_role()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_user_role()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Resurs egasi yoki admin role ga ega bo'lgan foydalanuvchiga ruxsat berish
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin har qanday resursga kirishi mumkin
        if request.user.is_admin_role():
            return True

        # Foydalanuvchi faqat o'z resurslariga kirishi mumkin
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'profile'):
            return obj.profile.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'student'):
            return obj.student == request.user
        else:
            # Agar obyektda user field'i bo'lmasa, 403 qaytarish
            return False


class IsVipOrAdmin(permissions.BasePermission):
    """
    VIP yoki admin role ga ega foydalanuvchilarga ruxsat berish
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin har doim ruxsatga ega
        if request.user.is_admin_role():
            return True

        # VIP foydalanuvchilar ruxsatga ega
        if hasattr(request.user, 'profile') and request.user.profile.is_vip_active():
            return True

        return False


class JWTAuthenticationWithRole(JWTAuthentication):
    """
    JWT token ichida role ni ham tekshirish
    """

    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)

        # Token ichidan role ni olish
        user_id = validated_token.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                validated_token['role'] = user.role
                validated_token['is_vip'] = user.profile.is_vip_active() if hasattr(user, 'profile') else False
                validated_token['coins'] = user.profile.coins if hasattr(user, 'profile') else 0
            except User.DoesNotExist:
                pass

        return validated_token


def check_user_permission(user, required_role=None):
    """
    Foydalanuvchi ruxsatini tekshirish funksiyasi
    """
    if not user or not user.is_authenticated:
        return False

    if required_role == 'admin':
        return user.is_admin_role()
    elif required_role == 'user':
        return user.is_user_role()

    return True


def check_vip_access(user):
    """
    VIP ruxsatini tekshirish
    """
    if not user or not user.is_authenticated:
        return False

    # Adminlar har doim VIP ga kirishi mumkin
    if user.is_admin_role():
        return True

    # VIP foydalanuvchilar
    if hasattr(user, 'profile') and user.profile.is_vip_active():
        return True

    return False
