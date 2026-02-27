from datetime import date, timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import UserDailyUsage
from subscriptions.services import SubscriptionService


User = get_user_model()


class DailyUsageService:
    """
    Kunlik foydalanish statistikasini boshqarish.
    """

    @staticmethod
    def get_or_create_today_usage(user: User) -> UserDailyUsage:
        today = timezone.localdate()
        usage, _ = UserDailyUsage.objects.get_or_create(user=user, date=today)
        return usage

    @staticmethod
    def increment_vocab(user: User, amount: int = 1) -> UserDailyUsage:
        usage = DailyUsageService.get_or_create_today_usage(user)
        usage.vocab_learned_count += amount
        usage.save(update_fields=["vocab_learned_count", "updated_at"])
        return usage

    @staticmethod
    def increment_writing_evaluation(user: User) -> UserDailyUsage:
        usage = DailyUsageService.get_or_create_today_usage(user)
        usage.writing_evaluation_count += 1
        usage.save(update_fields=["writing_evaluation_count", "updated_at"])
        return usage

    @staticmethod
    def increment_speaking_mock(user: User) -> UserDailyUsage:
        usage = DailyUsageService.get_or_create_today_usage(user)
        usage.speaking_mock_count += 1
        usage.save(update_fields=["speaking_mock_count", "updated_at"])
        return usage


class ProfileProgressService:
    """
    accounts.views.UserProfileView ichida ishlatiladigan service.
    Bu yerda streak va umumiy progress bo'yicha soddalashtirilgan ma'lumot qaytaramiz.
    """

    @staticmethod
    def get_streak(user: User) -> int:
        """
        Ketma-ket kunlar soni (bugundan orqaga qarab).
        """
        today = timezone.localdate()
        streak = 0
        current_date = today

        while True:
            if UserDailyUsage.objects.filter(user=user, date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak

    @staticmethod
    def get_profile_progress(user: User) -> dict:
        """
        accounts.UserProfileView uchun soddalashtirilgan progress obyekti.
        Keyinchalik bu yerga yana ko'proq statistika qo'shish mumkin.
        """
        today_usage = UserDailyUsage.objects.filter(
            user=user, date=timezone.localdate()
        ).first()
        active_subscription = SubscriptionService.get_active_subscription(user)

        return {
            "streak_days": ProfileProgressService.get_streak(user),
            "today": {
                "vocab_learned": today_usage.vocab_learned_count
                if today_usage
                else 0,
                "writing_evaluations": today_usage.writing_evaluation_count
                if today_usage
                else 0,
                "speaking_mocks": today_usage.speaking_mock_count
                if today_usage
                else 0,
            },
            "subscription": {
                "has_active": bool(active_subscription),
                "plan_code": active_subscription.plan.code
                if active_subscription and active_subscription.plan
                else None,
                "plan_name": active_subscription.plan.name
                if active_subscription and active_subscription.plan
                else None,
                "start_at": active_subscription.start_at if active_subscription else None,
                "end_at": active_subscription.end_at if active_subscription else None,
            },
        }


