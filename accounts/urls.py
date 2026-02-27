from django.urls import path
from .views import (
    UserRegistrationView, GoogleAuthView,
    PasswordResetView, PasswordResetConfirmView,
    EmailVerificationView, ResendVerificationEmailView,
    UserProfileView, ChangePasswordView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('google/', GoogleAuthView.as_view(), name='google-auth'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Email verification
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),

    # Password reset
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
