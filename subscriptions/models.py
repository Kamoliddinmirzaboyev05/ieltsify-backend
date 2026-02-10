from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class SubscriptionPlan(models.Model):
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    
    DURATION_CHOICES = (
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    priority = models.PositiveIntegerField(default=0, help_text="Ko'rsatish tartibi (qancha kichik bo'lsa, shuncha oldin)")
    
    is_active = models.BooleanField(default=True)
    is_vip = models.BooleanField(default=False)
    
    # VIP specific fields
    duration_days = models.PositiveIntegerField(help_text="Duration in days for calculation")
    features = models.JSONField(default=list, blank=True, help_text="List of features included in this plan")
    max_tests_per_day = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum tests allowed per day")
    max_study_materials = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum study materials allowed per month")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        vip_tag = "VIP " if self.is_vip else ""
        return f"{vip_tag}{self.name} - {self.get_duration_display()} - ${self.price}"
    
    def get_duration_days(self):
        if self.duration == self.WEEKLY:
            return 7
        elif self.duration == self.MONTHLY:
            return 30
        return 0
    
    class Meta:
        ordering = ['priority', 'price']
        db_table = 'subscriptions_subscription_plan'


class UserSubscription(models.Model):
    PENDING = 'pending'
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (CANCELLED, 'Cancelled'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='user_subscriptions')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    started_at = models.DateTimeField(auto_now_add=True, help_text="When the subscription was started")
    auto_renew = models.BooleanField(default=False, help_text="Auto-renew subscription")
    
    tests_used_today = models.PositiveIntegerField(default=0, help_text="Number of tests used today")
    study_materials_used = models.PositiveIntegerField(default=0, help_text="Number of study materials used")
    
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.get_status_display()})"
    
    def is_active(self):
        if self.status != self.ACTIVE:
            return False
        return self.expires_at > timezone.now()
    
    def days_remaining(self):
        if not self.is_active():
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    def coins_remaining(self):
        if self.plan.unlimited_coins:
            return float('inf')
        remaining = self.coins_awarded - self.coins_used
        return max(0, remaining)
    
    def activate(self):
        self.status = self.ACTIVE
        self.starts_at = timezone.now()
        self.expires_at = self.starts_at + timezone.timedelta(days=self.plan.get_duration_days())
        self.coins_awarded = self.plan.coins_bonus
        self.save()
        
        # Update user profile
        profile = self.user.profile
        if self.plan.is_vip:
            profile.is_vip = True
            profile.vip_expires_at = self.expires_at
        profile.save()
        
        return self.coins_awarded
    
    def expire(self):
        self.status = self.EXPIRED
        self.save()
        
        # Update user profile if this was a VIP subscription
        if self.plan.is_vip:
            profile = self.user.profile
            # Check if user has other active VIP subscriptions
            other_active_vip = UserSubscription.objects.filter(
                user=self.user,
                plan__is_vip=True,
                status=self.ACTIVE,
                expires_at__gt=timezone.now()
            ).exclude(id=self.id).exists()
            
            if not other_active_vip:
                profile.is_vip = False
                profile.vip_expires_at = None
            profile.save()
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'subscriptions_user_subscription'


class SubscriptionTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('card', 'Karta'),
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('uzum', 'Uzum Bank'),
        ('cash', 'Naqt pul'),
        ('coins', 'Coinlar'),
    )
    
    TRANSACTION_STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('completed', 'Bajarildi'),
        ('failed', 'Xatolik'),
        ('cancelled', 'Bekor qilindi'),
        ('refunded', 'Qaytarildi'),
    )
    
    TRANSACTION_TYPE_CHOICES = (
        ('subscription', 'Subscription'),
        ('renewal', 'Yangilash'),
        ('upgrade', 'Yangilash'),
        ('refund', 'Qaytarish'),
        ('bonus', 'Bonus'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='subscription_transactions')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Unique transaction identifier")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='subscription')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    gateway_response = models.JSONField(default=dict, blank=True, help_text="Payment gateway response data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'subscriptions_transaction'
