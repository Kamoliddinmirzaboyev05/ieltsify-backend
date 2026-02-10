# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Sum, Count, Avg
# from django.utils import timezone
# from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction
#
#
# @admin.register(SubscriptionPlan)
# class SubscriptionPlanAdmin(admin.ModelAdmin):
#     list_display = ('name', 'duration', 'price', 'coins_bonus', 'is_vip', 'is_active', 'subscription_type', 'created_at')
#     list_filter = ('duration', 'is_vip', 'is_active', 'created_at')
#     search_fields = ('name', 'description')
#     ordering = ('price',)
#     readonly_fields = ('created_at', 'updated_at')
#
#     fieldsets = (
#         ('Plan Information', {'fields': ('name', 'description')}),
#         ('Pricing', {'fields': ('duration', 'price')}),
#         ('Coin Settings', {'fields': ('coins_bonus',)}),
#         ('Plan Type', {'fields': ('is_vip', 'is_active')}),
#         ('VIP Features', {'fields': ('unlimited_coins', 'max_coins_per_month')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def subscription_type(self, obj):
#         if obj.is_vip:
#             if obj.unlimited_coins:
#                 return format_html(
#                     '<span style="color: purple; font-weight: bold;">VIP Unlimited</span>'
#                 )
#             else:
#                 return format_html(
#                     '<span style="color: blue; font-weight: bold;">VIP Limited</span>'
#                 )
#         return format_html(
#             '<span style="color: green;">Standard</span>'
#         )
#     subscription_type.short_description = 'Type'
#
#     actions = ['activate_selected', 'deactivate_selected', 'duplicate_plan']
#
#     def activate_selected(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_active=True)
#         messages.success(request, f'{count} ta subscription plani aktive qilindi')
#     activate_selected.short_description = 'Tanlangan planlarni aktive qilish'
#
#     def deactivate_selected(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_active=False)
#         messages.success(request, f'{count} ta subscription plani nofaol qilindi')
#     deactivate_selected.short_description = 'Tanlangan planlarni nofaol qilish'
#
#     def duplicate_plan(self, request, queryset):
#         from django.contrib import messages
#
#         count = 0
#         for plan in queryset:
#             plan.pk = None
#             plan.name = f"{plan.name} (Copy)"
#             plan.save()
#             count += 1
#
#         messages.success(request, f'{count} ta subscription plani nusxalandi')
#     duplicate_plan.short_description = 'Tanlangan planlarni nusxalash'
#
#
# @admin.register(UserSubscription)
# class UserSubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'plan_name', 'status', 'subscription_period', 'days_remaining', 'coins_info', 'created_at')
#     list_filter = ('status', 'plan__duration', 'plan__is_vip', 'created_at', 'starts_at', 'expires_at')
#     search_fields = ('user__email', 'user__username', 'plan__name')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'updated_at', 'days_remaining_calc', 'coins_remaining_calc')
#
#     fieldsets = (
#         ('Subscription Information', {'fields': ('user', 'plan', 'status')}),
#         ('Period', {'fields': ('starts_at', 'expires_at')}),
#         ('Coin Information', {'fields': ('coins_awarded', 'coins_used')}),
#         ('Payment Details', {'fields': ('payment_id', 'payment_amount')}),
#         ('Calculated Fields', {'fields': ('days_remaining_calc', 'coins_remaining_calc')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User Email'
#     user_email.admin_order_field = 'user__email'
#
#     def plan_name(self, obj):
#         vip_tag = "👑 " if obj.plan.is_vip else ""
#         return f"{vip_tag}{obj.plan.name}"
#     plan_name.short_description = 'Plan'
#     plan_name.admin_order_field = 'plan__name'
#
#     def subscription_period(self, obj):
#         return obj.plan.get_duration_display()
#     subscription_period.short_description = 'Period'
#
#     def days_remaining(self, obj):
#         days = obj.days_remaining()
#         if days > 30:
#             return format_html(
#                 '<span style="color: green; font-weight: bold;">{} days</span>',
#                 days
#             )
#         elif days > 7:
#             return format_html(
#                 '<span style="color: orange; font-weight: bold;">{} days</span>',
#                 days
#             )
#         elif days > 0:
#             return format_html(
#                 '<span style="color: red; font-weight: bold;">{} days</span>',
#                 days
#             )
#         return format_html(
#             '<span style="color: gray;">Expired</span>'
#         )
#     days_remaining.short_description = 'Days Left'
#
#     def coins_info(self, obj):
#         remaining = obj.coins_remaining()
#         if remaining == float('inf'):
#             return format_html(
#                 '<span style="color: purple; font-weight: bold;">♾️ Unlimited</span>'
#             )
#         elif remaining > 100:
#             return format_html(
#                 '<span style="color: green;">{}/{} coins</span>',
#                 remaining, obj.coins_awarded
#             )
#         elif remaining > 20:
#             return format_html(
#                 '<span style="color: orange;">{}/{} coins</span>',
#                 remaining, obj.coins_awarded
#             )
#         else:
#             return format_html(
#                 '<span style="color: red; font-weight: bold;">{}/{} coins</span>',
#                 remaining, obj.coins_awarded
#             )
#     coins_info.short_description = 'Coins'
#
#     def days_remaining_calc(self, obj):
#         return f"{obj.days_remaining()} days"
#     days_remaining_calc.short_description = 'Days Remaining'
#
#     def coins_remaining_calc(self, obj):
#         remaining = obj.coins_remaining()
#         if remaining == float('inf'):
#             return "Unlimited"
#         return f"{remaining} coins"
#     coins_remaining_calc.short_description = 'Coins Remaining'
#
#     actions = ['activate_selected', 'expire_selected', 'extend_subscription', 'add_bonus_coins']
#
#     def activate_selected(self, request, queryset):
#         from django.contrib import messages
#
#         count = 0
#         for subscription in queryset:
#             if subscription.status != 'active':
#                 coins_awarded = subscription.activate()
#                 # Coin transaction yaratish
#                 from accounts.models import CoinTransaction
#                 CoinTransaction.objects.create(
#                     user=subscription.user,
#                     amount=coins_awarded,
#                     type='in',
#                     reason='subscription',
#                     description=f'Subscription activation: {subscription.plan.name}',
#                     related_subscription=subscription
#                 )
#                 count += 1
#
#         messages.success(request, f'{count} ta subscription aktive qilindi')
#     activate_selected.short_description = 'Tanlangan subscriptionlarni aktive qilish'
#
#     def expire_selected(self, request, queryset):
#         from django.contrib import messages
#
#         count = 0
#         for subscription in queryset:
#             if subscription.status == 'active':
#                 subscription.expire()
#                 count += 1
#
#         messages.success(request, f'{count} ta subscription expired qilindi')
#     expire_selected.short_description = 'Tanlangan subscriptionlarni expired qilish'
#
#     def extend_subscription(self, request, queryset):
#         from django.contrib import messages
#         from datetime import timedelta
#
#         count = 0
#         for subscription in queryset:
#             subscription.expires_at += timedelta(days=30)
#             subscription.save()
#             count += 1
#
#         messages.success(request, f'{count} ta subscription 30 kunga uzaytirildi')
#     extend_subscription.short_description = 'Subscriptionlarni 30 kunga uzaytirish'
#
#     def add_bonus_coins(self, request, queryset):
#         from django.contrib import messages
#         from accounts.models import CoinTransaction
#
#         bonus_amount = 100  # Bonus coin miqdori
#         count = 0
#
#         for subscription in queryset:
#             subscription.coins_awarded += bonus_amount
#             subscription.save()
#
#             # Coin transaction yaratish
#             CoinTransaction.objects.create(
#                 user=subscription.user,
#                 amount=bonus_amount,
#                 type='in',
#                 reason='admin_adjustment',
#                 description=f'Admin bonus coins: {subscription.plan.name}',
#                 related_subscription=subscription
#             )
#
#             # User profile coins ham qo'shish
#             profile = subscription.user.profile
#             profile.coins += bonus_amount
#             profile.save()
#
#             count += 1
#
#         messages.success(request, f'{count} ta subscriptionga {bonus_amount} ta coin bonus qo\'shildi')
#     add_bonus_coins.short_description = f'100 ta coin bonus qo\'shish'
#
#
# @admin.register(SubscriptionTransaction)
# class SubscriptionTransactionAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'subscription_info', 'amount', 'currency', 'payment_method', 'status', 'created_at')
#     list_filter = ('status', 'payment_method', 'currency', 'created_at')
#     search_fields = ('user__email', 'user__username', 'payment_id', 'subscription__plan__name')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at',)
#
#     fieldsets = (
#         ('Transaction Information', {'fields': ('user', 'subscription')}),
#         ('Payment Details', {'fields': ('amount', 'currency', 'payment_method', 'payment_id', 'status')}),
#         ('Timestamp', {'fields': ('created_at',)}),
#     )
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User Email'
#     user_email.admin_order_field = 'user__email'
#
#     def subscription_info(self, obj):
#         return f"{obj.subscription.plan.name} ({obj.subscription.plan.get_duration_display()})"
#     subscription_info.short_description = 'Subscription'
#
#     actions = ['mark_successful', 'mark_failed', 'export_transactions']
#
#     def mark_successful(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(status='successful')
#         messages.success(request, f'{count} ta transaction successful deb belgilandi')
#     mark_successful.short_description = 'Successful deb belgilash'
#
#     def mark_failed(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(status='failed')
#         messages.success(request, f'{count} ta transaction failed deb belgilandi')
#     mark_failed.short_description = 'Failed deb belgilash'
#
#     def export_transactions(self, request, queryset):
#         import csv
#         from django.http import HttpResponse
#
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="subscription_transactions.csv"'
#
#         writer = csv.writer(response)
#         writer.writerow(['User Email', 'Subscription Plan', 'Amount', 'Currency', 'Payment Method', 'Payment ID', 'Status', 'Created At'])
#
#         for transaction in queryset:
#             writer.writerow([
#                 transaction.user.email,
#                 transaction.subscription.plan.name,
#                 transaction.amount,
#                 transaction.currency,
#                 transaction.payment_method,
#                 transaction.payment_id,
#                 transaction.status,
#                 transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
#             ])
#
#         return response
#     export_transactions.short_description = 'Export selected transactions to CSV'
