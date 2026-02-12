from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    is_google_user = models.BooleanField(default=False)

    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    def is_user_role(self):
        return self.role == self.ROLE_USER


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')

    email_verified = models.BooleanField(default=False)


    target_band_score = models.FloatField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    listening_score = models.FloatField(default=0)
    reading_score = models.FloatField(default=0)
    writing_score = models.FloatField(default=0)
    speaking_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}"

    def has_unlimited_access(self):
        """Foydalanuvchining cheksiz kirish huquqi borligini tekshirish"""
        # Hozircha false qaytaramiz, keyinchalik subscription ga bog'lash mumkin
        return False


    class Meta:
        ordering = ['-created_at']
        db_table = 'accounts_user_profile'
