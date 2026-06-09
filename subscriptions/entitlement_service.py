"""
EntitlementService — Material va xizmatlarning foydalanuvchi uchun ochiq/yopiq ekanini tekshiradi.
UsageLimitService — Kunlik/haftalik limitlarni tekshiradi.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models as db_models
from datetime import timedelta

from .models import (
    SubscriptionPlan, UserSubscription, CoinWallet,
    CoinServiceCost, CoinTransaction
)
from attempts.models import UserDailyUsage

User = get_user_model()


class EntitlementService:
    """
    Foydalanuvchining material yoki xizmatga kirish huquqini tekshiradi.
    Har bir tekshiruv natijasi:
    {
        'allowed': True/False,
        'reason': 'subscription_active' | 'daily_limit_reached' | 'requires_subscription' | ...,
        'remaining_quota': 5,
        'requires_coin': False,
        'required_coin': 0,
    }
    """

    @staticmethod
    def get_active_subscription(user) -> UserSubscription | None:
        """Foydalanuvchining joriy aktiv obunasini olish"""
        now = timezone.now()
        return UserSubscription.objects.filter(
            user=user,
            is_active=True,
            start_at__lte=now,
            end_at__gte=now,
        ).select_related('plan').first()

    @staticmethod
    def get_user_plan(user) -> SubscriptionPlan:
        """Foydalanuvchining joriy tarifi (obuna bo'lmasa Free)"""
        sub = EntitlementService.get_active_subscription(user)
        if sub and sub.plan:
            return sub.plan
        # Free plan
        return SubscriptionPlan.objects.filter(code='free').first()

    @staticmethod
    def can_access_reading(user) -> dict:
        """Reading passage ochish mumkinmi?"""
        plan = EntitlementService.get_user_plan(user)
        if not plan:
            return {'allowed': False, 'reason': 'no_plan'}

        if plan.is_unlimited_reading:
            # Fair-use limit tekshirish
            today_usage = UsageLimitService.get_today_reading_count(user)
            if today_usage >= plan.daily_reading_limit:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_reached',
                    'remaining_quota': 0,
                    'message': 'Bugungi Reading limitingiz tugadi. Ertaga yana ochiladi.',
                }
            return {
                'allowed': True,
                'reason': 'subscription_active',
                'remaining_quota': plan.daily_reading_limit - today_usage,
            }
        else:
            # Free user — kunlik limit
            today_usage = UsageLimitService.get_today_reading_count(user)
            if today_usage >= plan.daily_reading_limit:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_reached',
                    'remaining_quota': 0,
                    'requires_subscription': True,
                    'message': 'Bugungi bepul Reading limitingiz tugadi.',
                }
            return {
                'allowed': True,
                'reason': 'free_quota',
                'remaining_quota': plan.daily_reading_limit - today_usage,
            }

    @staticmethod
    def can_access_listening(user) -> dict:
        """Listening section ochish mumkinmi?"""
        plan = EntitlementService.get_user_plan(user)
        if not plan:
            return {'allowed': False, 'reason': 'no_plan'}

        if plan.is_unlimited_listening:
            today_usage = UsageLimitService.get_today_listening_count(user)
            if today_usage >= plan.daily_listening_limit:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_reached',
                    'remaining_quota': 0,
                    'message': 'Bugungi Listening limitingiz tugadi.',
                }
            return {
                'allowed': True,
                'reason': 'subscription_active',
                'remaining_quota': plan.daily_listening_limit - today_usage,
            }
        else:
            today_usage = UsageLimitService.get_today_listening_count(user)
            if today_usage >= plan.daily_listening_limit:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_reached',
                    'remaining_quota': 0,
                    'requires_subscription': True,
                    'message': 'Bugungi bepul Listening limitingiz tugadi.',
                }
            return {
                'allowed': True,
                'reason': 'free_quota',
                'remaining_quota': plan.daily_listening_limit - today_usage,
            }

    @staticmethod
    def can_use_writing_ai(user, writing_type: str = 'writing_task2') -> dict:
        """Writing AI tahlilidan foydalanish mumkinmi?"""
        plan = EntitlementService.get_user_plan(user)
        sub = EntitlementService.get_active_subscription(user)

        # Tarif ichidagi limit tekshirish
        if sub and plan and plan.writing_ai_limit > 0:
            period_usage = UsageLimitService.get_period_writing_ai_count(user, sub)
            if period_usage < plan.writing_ai_limit:
                # Kunlik fair-use limit
                today_usage = UsageLimitService.get_today_writing_ai_count(user)
                if today_usage >= plan.daily_writing_ai_limit:
                    return {
                        'allowed': False,
                        'reason': 'daily_limit_reached',
                        'remaining_quota': 0,
                        'message': 'Bugungi Writing AI limitingiz tugadi. Ertaga davom eting.',
                    }
                return {
                    'allowed': True,
                    'reason': 'subscription_quota',
                    'remaining_quota': plan.writing_ai_limit - period_usage,
                    'requires_coin': False,
                }

        # Tarif limiti tugagan yoki free user — coin kerak
        cost = CoinServiceCost.objects.filter(service_code=writing_type, is_active=True).first()
        coin_cost = cost.cost_coins if cost else 10

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        if wallet_balance >= coin_cost:
            return {
                'allowed': True,
                'reason': 'coin_available',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'balance_after': wallet_balance - coin_cost,
            }
        else:
            return {
                'allowed': False,
                'reason': 'insufficient_coin',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'message': f'Balansingiz yetarli emas. {coin_cost} coin kerak, sizda {wallet_balance} coin bor.',
            }

    @staticmethod
    def can_use_speaking_ai(user, speaking_type: str = 'speaking_part1') -> dict:
        """Speaking AI tahlilidan foydalanish mumkinmi?"""
        plan = EntitlementService.get_user_plan(user)
        sub = EntitlementService.get_active_subscription(user)

        if sub and plan and plan.speaking_ai_limit > 0:
            period_usage = UsageLimitService.get_period_speaking_ai_count(user, sub)
            if period_usage < plan.speaking_ai_limit:
                today_usage = UsageLimitService.get_today_speaking_ai_count(user)
                if today_usage >= plan.daily_speaking_ai_limit:
                    return {
                        'allowed': False,
                        'reason': 'daily_limit_reached',
                        'remaining_quota': 0,
                        'message': 'Bugungi Speaking AI limitingiz tugadi.',
                    }
                return {
                    'allowed': True,
                    'reason': 'subscription_quota',
                    'remaining_quota': plan.speaking_ai_limit - period_usage,
                    'requires_coin': False,
                }

        cost = CoinServiceCost.objects.filter(service_code=speaking_type, is_active=True).first()
        coin_cost = cost.cost_coins if cost else 6

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        if wallet_balance >= coin_cost:
            return {
                'allowed': True,
                'reason': 'coin_available',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'balance_after': wallet_balance - coin_cost,
            }
        else:
            return {
                'allowed': False,
                'reason': 'insufficient_coin',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'message': f'Balansingiz yetarli emas. {coin_cost} coin kerak.',
            }

    @staticmethod
    def get_usage_limits_summary(user) -> dict:
        """Dashboard uchun barcha limitlar xulosa"""
        plan = EntitlementService.get_user_plan(user)
        sub = EntitlementService.get_active_subscription(user)

        today_reading = UsageLimitService.get_today_reading_count(user)
        today_listening = UsageLimitService.get_today_listening_count(user)

        writing_used = 0
        speaking_used = 0
        writing_limit = 0
        speaking_limit = 0

        if sub and plan:
            writing_used = UsageLimitService.get_period_writing_ai_count(user, sub)
            speaking_used = UsageLimitService.get_period_speaking_ai_count(user, sub)
            writing_limit = plan.writing_ai_limit
            speaking_limit = plan.speaking_ai_limit

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        return {
            'plan_code': plan.code if plan else 'free',
            'plan_name': plan.name if plan else 'Free',
            'subscription_active': sub is not None,
            'subscription_end_date': sub.end_at.isoformat() if sub else None,
            'days_remaining': (sub.end_at - timezone.now()).days if sub else None,
            'daily_reading': {
                'used': today_reading,
                'limit': plan.daily_reading_limit if plan else 1,
                'is_unlimited': plan.is_unlimited_reading if plan else False,
            },
            'daily_listening': {
                'used': today_listening,
                'limit': plan.daily_listening_limit if plan else 1,
                'is_unlimited': plan.is_unlimited_listening if plan else False,
            },
            'writing_ai': {
                'used': writing_used,
                'limit': writing_limit,
                'remaining': max(0, writing_limit - writing_used),
            },
            'speaking_ai': {
                'used': speaking_used,
                'limit': speaking_limit,
                'remaining': max(0, speaking_limit - speaking_used),
            },
            'coin_balance': wallet_balance,
        }


class UsageLimitService:
    """Kunlik va davr bo'yicha foydalanish hisoblagichi"""

    @staticmethod
    def get_today_usage(user) -> UserDailyUsage:
        today = timezone.now().date()
        usage, _ = UserDailyUsage.objects.get_or_create(user=user, date=today)
        return usage

    @staticmethod
    def get_today_reading_count(user) -> int:
        usage = UsageLimitService.get_today_usage(user)
        return usage.reading_attempt_count

    @staticmethod
    def get_today_listening_count(user) -> int:
        usage = UsageLimitService.get_today_usage(user)
        return usage.listening_attempt_count

    @staticmethod
    def get_today_writing_ai_count(user) -> int:
        usage = UsageLimitService.get_today_usage(user)
        return usage.writing_evaluation_count

    @staticmethod
    def get_today_speaking_ai_count(user) -> int:
        usage = UsageLimitService.get_today_usage(user)
        return usage.speaking_mock_count

    @staticmethod
    def get_period_writing_ai_count(user, subscription: UserSubscription) -> int:
        """Obuna davri ichidagi Writing AI foydalanish soni"""
        if not subscription or not subscription.start_at:
            return 0
        from django.db.models import Sum
        return UserDailyUsage.objects.filter(
            user=user,
            date__gte=subscription.start_at.date(),
        ).aggregate(total=Sum('writing_evaluation_count'))['total'] or 0

    @staticmethod
    def get_period_speaking_ai_count(user, subscription: UserSubscription) -> int:
        """Obuna davri ichidagi Speaking AI foydalanish soni"""
        if not subscription or not subscription.start_at:
            return 0
        from django.db.models import Sum
        return UserDailyUsage.objects.filter(
            user=user,
            date__gte=subscription.start_at.date(),
        ).aggregate(total=Sum('speaking_mock_count'))['total'] or 0

    @staticmethod
    def increment_reading(user):
        usage = UsageLimitService.get_today_usage(user)
        usage.reading_attempt_count += 1
        usage.save(update_fields=['reading_attempt_count', 'updated_at'])

    @staticmethod
    def increment_listening(user):
        usage = UsageLimitService.get_today_usage(user)
        usage.listening_attempt_count += 1
        usage.save(update_fields=['listening_attempt_count', 'updated_at'])

    @staticmethod
    def increment_writing_ai(user):
        usage = UsageLimitService.get_today_usage(user)
        usage.writing_evaluation_count += 1
        usage.save(update_fields=['writing_evaluation_count', 'updated_at'])

    @staticmethod
    def increment_speaking_ai(user):
        usage = UsageLimitService.get_today_usage(user)
        usage.speaking_mock_count += 1
        usage.save(update_fields=['speaking_mock_count', 'updated_at'])
