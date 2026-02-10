# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.db import transaction
# from django.conf import settings
# import logging
# from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction
# from accounts.services import CoinService
#
# logger = logging.getLogger(__name__)
#
#
# class SubscriptionService:
#     """Subscriptionlar bilan ishlash uchun service klassi"""
#
#     @staticmethod
#     def get_available_plans():
#         """Mavjud subscription planlarini olish"""
#         return SubscriptionPlan.objects.filter(
#             is_active=True
#         ).order_by('priority', 'price')
#
#     @staticmethod
#     def get_plan_by_id(plan_id):
#         """ID bo'yicha subscription planini olish"""
#         try:
#             return SubscriptionPlan.objects.get(id=plan_id, is_active=True)
#         except SubscriptionPlan.DoesNotExist:
#             return None
#
#     @staticmethod
#     def create_subscription(user, plan_id, payment_method, auto_renew=False):
#         """Yangi subscription yaratish"""
#         try:
#             with transaction.atomic():
#                 plan = SubscriptionService.get_plan_by_id(plan_id)
#                 if not plan:
#                     raise ValueError("Subscription plan topilmadi")
#
#                 # Active subscription borligini tekshirish
#                 active_subscription = UserSubscription.objects.filter(
#                     user=user,
#                     status='active'
#                 ).first()
#
#                 if active_subscription:
#                     raise ValueError("Foydalanuvchida allaqachon active subscription mavjud")
#
#                 # User subscription yaratish
#                 user_subscription = UserSubscription.objects.create(
#                     user=user,
#                     plan=plan,
#                     status='active',
#                     started_at=timezone.now(),
#                     expires_at=timezone.now() + timedelta(days=plan.duration_days),
#                     auto_renew=auto_renew
#                 )
#
#                 # Transaction yaratish
#                 transaction_record = SubscriptionTransaction.objects.create(
#                     user=user,
#                     plan=plan,
#                     transaction_type='subscription',
#                     amount=plan.price,
#                     payment_method=payment_method,
#                     status='completed',
#                     transaction_id=f"SUB_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#                 )
#
#                 logger.info(f"Subscription created: {user.email} -> {plan.name}")
#                 return user_subscription, transaction_record
#
#         except Exception as e:
#             logger.error(f"Error creating subscription: {str(e)}")
#             raise
#
#     @staticmethod
#     def renew_subscription(user, payment_method):
#         """Subscriptionni yangilash"""
#         try:
#             with transaction.atomic():
#                 current_subscription = UserSubscription.objects.filter(
#                     user=user,
#                     status='active'
#                 ).first()
#
#                 if not current_subscription:
#                     raise ValueError("Active subscription topilmadi")
#
#                 plan = current_subscription.plan
#
#                 # Expiration date ni yangilash
#                 if current_subscription.expires_at > timezone.now():
#                     # Muddati tugamagan, qo'shib yuborish
#                     new_expires_at = current_subscription.expires_at + timedelta(days=plan.duration_days)
#                 else:
#                     # Muddati tugagan, boshidan boshlash
#                     new_expires_at = timezone.now() + timedelta(days=plan.duration_days)
#
#                 current_subscription.expires_at = new_expires_at
#                 current_subscription.status = 'active'
#                 current_subscription.save()
#
#                 # Transaction yaratish
#                 transaction_record = SubscriptionTransaction.objects.create(
#                     user=user,
#                     plan=plan,
#                     transaction_type='renewal',
#                     amount=plan.price,
#                     payment_method=payment_method,
#                     status='completed',
#                     transaction_id=f"REN_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#                 )
#
#                 logger.info(f"Subscription renewed: {user.email} -> {plan.name}")
#                 return current_subscription, transaction_record
#
#         except Exception as e:
#             logger.error(f"Error renewing subscription: {str(e)}")
#             raise
#
#     @staticmethod
#     def cancel_subscription(user, reason=None, immediate=False):
#         """Subscriptionni bekor qilish"""
#         try:
#             with transaction.atomic():
#                 subscription = UserSubscription.objects.filter(
#                     user=user,
#                     status='active'
#                 ).first()
#
#                 if not subscription:
#                     raise ValueError("Active subscription topilmadi")
#
#                 if immediate:
#                     # Darhol bekor qilish
#                     subscription.status = 'cancelled'
#                     subscription.expires_at = timezone.now()
#                 else:
#                     # Muddati tugaganda bekor qilish
#                     subscription.status = 'cancelled'
#                     subscription.auto_renew = False
#
#                 subscription.save()
#
#                 # Transaction yaratish
#                 transaction_record = SubscriptionTransaction.objects.create(
#                     user=user,
#                     plan=subscription.plan,
#                     transaction_type='cancellation',
#                     amount=0,
#                     payment_method='none',
#                     status='completed',
#                     transaction_id=f"CAN_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#                 )
#
#                 logger.info(f"Subscription cancelled: {user.email} -> {subscription.plan.name}")
#                 return subscription, transaction_record
#
#         except Exception as e:
#             logger.error(f"Error cancelling subscription: {str(e)}")
#             raise
#
#     @staticmethod
#     def upgrade_subscription(user, new_plan_id, payment_method):
#         """Subscriptionni yangilash (upgrade)"""
#         try:
#             with transaction.atomic():
#                 current_subscription = UserSubscription.objects.filter(
#                     user=user,
#                     status='active'
#                 ).first()
#
#                 if not current_subscription:
#                     raise ValueError("Active subscription topilmadi")
#
#                 new_plan = SubscriptionService.get_plan_by_id(new_plan_id)
#                 if not new_plan:
#                     raise ValueError("Yangi plan topilmadi")
#
#                 # Yangi plan qimmatroq bo'lishi kerak
#                 if new_plan.price <= current_subscription.plan.price:
#                     raise ValueError("Yangi plan joriy plandan qimmatroq bo'lishi kerak")
#
#                 # Price difference ni hisoblash
#                 price_difference = new_plan.price - current_subscription.plan.price
#
#                 # Qolgan kunlarni hisoblash
#                 remaining_days = (current_subscription.expires_at - timezone.now()).days
#                 if remaining_days < 0:
#                     remaining_days = 0
#
#                 # Pro-rated refund (agar kerak bo'lsa)
#                 # Bu yerda oddiy upgrade logic
#
#                 # Subscriptionni yangilash
#                 current_subscription.plan = new_plan
#                 current_subscription.save()
#
#                 # Transaction yaratish
#                 transaction_record = SubscriptionTransaction.objects.create(
#                     user=user,
#                     plan=new_plan,
#                     transaction_type='upgrade',
#                     amount=price_difference,
#                     payment_method=payment_method,
#                     status='completed',
#                     transaction_id=f"UPG_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#                 )
#
#                 logger.info(f"Subscription upgraded: {user.email} -> {new_plan.name}")
#                 return current_subscription, transaction_record
#
#         except Exception as e:
#             logger.error(f"Error upgrading subscription: {str(e)}")
#             raise
#
#     @staticmethod
#     def get_user_subscription(user):
#         """Foydalanuvchining subscriptionini olish"""
#         return UserSubscription.objects.filter(
#             user=user
#         ).order_by('-created_at').first()
#
#     @staticmethod
#     def get_active_subscription(user):
#         """Foydalanuvchining active subscriptionini olish"""
#         return UserSubscription.objects.filter(
#             user=user,
#             status='active'
#         ).first()
#
#     @staticmethod
#     def check_subscription_limits(user, test_type='test'):
#         """Subscription limitlarini tekshirish"""
#         active_subscription = SubscriptionService.get_active_subscription(user)
#
#         if not active_subscription:
#             return False, "Active subscription mavjud emas"
#
#         if active_subscription.is_expired():
#             return False, "Subscription muddati tugagan"
#
#         if test_type == 'test':
#             if active_subscription.plan.max_tests_per_day > 0:
#                 if active_subscription.tests_used_today >= active_subscription.plan.max_tests_per_day:
#                     return False, "Kunlik test limiti to'ldi"
#
#         elif test_type == 'study_material':
#             if active_subscription.plan.max_study_materials > 0:
#                 if active_subscription.study_materials_used >= active_subscription.plan.max_study_materials:
#                     return False, "Study material limiti to'ldi"
#
#         return True, "Limitlar normal"
#
#     @staticmethod
#     def increment_usage(user, usage_type='test'):
#         """Usage count ni oshirish"""
#         active_subscription = SubscriptionService.get_active_subscription(user)
#
#         if active_subscription:
#             if usage_type == 'test':
#                 active_subscription.tests_used_today += 1
#             elif usage_type == 'study_material':
#                 active_subscription.study_materials_used += 1
#
#             active_subscription.save()
#
#     @staticmethod
#     def reset_daily_usage():
#         """Kunlik usage larni qayta tiklash (har kuni ishga tushirish kerak)"""
#         UserSubscription.objects.filter(
#             status='active'
#         ).update(tests_used_today=0)
#
#         logger.info("Daily usage reset completed")
#
#     @staticmethod
#     def check_expired_subscriptions():
#         """Muddati tugagan subscriptionlarni tekshirish"""
#         expired_subscriptions = UserSubscription.objects.filter(
#             status='active',
#             expires_at__lt=timezone.now()
#         )
#
#         for subscription in expired_subscriptions:
#             subscription.status = 'expired'
#             subscription.save()
#
#             # Auto-renew logic
#             if subscription.auto_renew:
#                 try:
#                     # Bu yerda auto-renew payment logic bo'lishi kerak
#                     # Hozircha log qilamiz
#                     logger.info(f"Auto-renew needed for: {subscription.user.email}")
#                 except Exception as e:
#                     logger.error(f"Auto-renew failed for {subscription.user.email}: {str(e)}")
#
#         logger.info(f"Processed {expired_subscriptions.count()} expired subscriptions")
#         return expired_subscriptions.count()
#
#     @staticmethod
#     def get_subscription_stats():
#         """Subscription statistikasini olish"""
#         total_subscriptions = UserSubscription.objects.count()
#         active_subscriptions = UserSubscription.objects.filter(status='active').count()
#         expired_subscriptions = UserSubscription.objects.filter(status='expired').count()
#         cancelled_subscriptions = UserSubscription.objects.filter(status='cancelled').count()
#
#         # Revenue calculations
#         total_revenue = SubscriptionTransaction.objects.filter(
#             status='completed'
#         ).aggregate(total=models.Sum('amount'))['total'] or 0
#
#         # Current month revenue
#         current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         current_month_revenue = SubscriptionTransaction.objects.filter(
#             status='completed',
#             created_at__gte=current_month_start
#         ).aggregate(total=models.Sum('amount'))['total'] or 0
#
#         # Most popular plan
#         most_popular_plan = UserSubscription.objects.filter(
#             status='active'
#         ).values('plan__name', 'plan__id').annotate(
#             count=models.Count('id')
#         ).order_by('-count').first()
#
#         return {
#             'total_subscriptions': total_subscriptions,
#             'active_subscriptions': active_subscriptions,
#             'expired_subscriptions': expired_subscriptions,
#             'cancelled_subscriptions': cancelled_subscriptions,
#             'total_revenue': total_revenue,
#             'current_month_revenue': current_month_revenue,
#             'most_popular_plan': most_popular_plan
#         }
#
#     @staticmethod
#     def get_payment_history(user, limit=50):
#         """To'lov tarixini olish"""
#         return SubscriptionTransaction.objects.filter(
#             user=user
#         ).order_by('-created_at')[:limit]
#
#     @staticmethod
#     def process_payment(user, plan, payment_method, transaction_type='subscription'):
#         """To'lovni qayta ishlash"""
#         try:
#             # Bu yerda payment gateway integration bo'lishi kerak
#             # Hozircha mock implementation
#
#             if payment_method == 'coin':
#                 # Coin bilan to'lov
#                 if user.userprofile.coins >= plan.price:
#                     CoinService.spend_coins(
#                         user,
#                         plan.price,
#                         f"Subscription payment: {plan.name}"
#                     )
#                     return True, "Coin bilan to'lov muvaffaqiyatli"
#                 else:
#                     return False, "Yetarli coin mavjud emas"
#
#             elif payment_method in ['click', 'payme', 'uzcard']:
#                 # Real payment gateway integration
#                 # Hozircha success deb qaytaramiz
#                 return True, f"{payment_method} bilan to'lov muvaffaqiyatli"
#
#             else:
#                 return False, "Noto'g'ri to'lov usuli"
#
#         except Exception as e:
#             logger.error(f"Payment processing error: {str(e)}")
#             return False, f"To'lovni qayta ishlashda xatolik: {str(e)}"
#
#
# class SubscriptionNotificationService:
#     """Subscription notificationlar uchun service"""
#
#     @staticmethod
#     def send_expiration_reminder():
#         """Subscription muddati tugashidan oldin eslatma yuborish"""
#         # 3 kun qolganlar
#         three_days_left = timezone.now() + timedelta(days=3)
#         subscriptions = UserSubscription.objects.filter(
#             status='active',
#             expires_at__date=three_days_left.date()
#         )
#
#         for subscription in subscriptions:
#             # Email yuborish logic
#             logger.info(f"Expiration reminder sent to: {subscription.user.email}")
#
#         # 1 kun qolganlar
#         one_day_left = timezone.now() + timedelta(days=1)
#         subscriptions = UserSubscription.objects.filter(
#             status='active',
#             expires_at__date=one_day_left.date()
#         )
#
#         for subscription in subscriptions:
#             # Email yuborish logic
#             logger.info(f"Expiration reminder sent to: {subscription.user.email}")
#
#     @staticmethod
#     def send_welcome_email(user_subscription):
#         """Yangi subscription uchun xush kelibsiz emaili"""
#         # Email yuborish logic
#         logger.info(f"Welcome subscription email sent to: {user_subscription.user.email}")
#
#     @staticmethod
#     def send_cancellation_email(user_subscription, reason=None):
#         """Subscription bekor qilish emaili"""
#         # Email yuborish logic
#         logger.info(f"Cancellation email sent to: {user_subscription.user.email}")
