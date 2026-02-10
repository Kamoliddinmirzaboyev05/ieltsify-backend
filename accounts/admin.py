from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_google_user', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_google_user', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Google Authentication', {'fields': ('google_id', 'is_google_user')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'is_vip', 'vip_status', 'created_at')
    list_filter = ('is_vip', 'created_at')
    search_fields = ('user__email', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('VIP Status', {'fields': ('is_vip', 'vip_expires_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def vip_status(self, obj):
        if obj.is_vip_active():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active ({})</span>',
                obj.vip_expires_at.strftime('%Y-%m-%d') if obj.vip_expires_at else 'No expiry'
            )
        elif obj.is_vip:
            return '<span style="color: orange; font-weight: bold;">⚠ Expired</span>'
        return '<span style="color: red;">✗ Not VIP</span>'
    vip_status.short_description = 'VIP Status'
    
    actions = ['activate_vip', 'deactivate_vip']
    
    def activate_vip(self, request, queryset):
        from django.contrib import messages
        from django.utils import timezone
        from datetime import timedelta
        
        count = 0
        for profile in queryset:
            profile.is_vip = True
            profile.vip_expires_at = timezone.now() + timedelta(days=30)
            profile.save()
            count += 1
        
        messages.success(request, f'{count} ta foydalanuvchi VIP ga aktive qilindi')
    activate_vip.short_description = 'VIP statusini aktive qilish (30 kun)'
    
    def deactivate_vip(self, request, queryset):
        from django.contrib import messages
        
        count = queryset.update(is_vip=False, vip_expires_at=None)
        messages.success(request, f'{count} ta foydalanuvchining VIP statusi o\'chirildi')
    deactivate_vip.short_description = 'VIP statusini o\'chirish'
