"""
MockExamService — Full Mock Exam biznes logikasi.
Quota tekshirish, coin reservation, attempt boshqarish.
"""
import uuid
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from .models import (
    MockExam, MockExamQuota, MockExamAttempt,
    MockExamAnswer, MockWritingSubmission, MockSpeakingRecording, MockExamResult
)
from subscriptions.models import CoinServiceCost, CoinWallet, CoinTransaction, UserSubscription
from subscriptions.services import WalletService
from subscriptions.entitlement_service import EntitlementService

User = get_user_model()


class MockExamService:
    """Full Mock Exam uchun asosiy servis."""

    @staticmethod
    def get_available_mocks(user, exam_type=None, mock_type=None):
        """Mavjud mock imtihonlar ro'yxati."""
        qs = MockExam.objects.filter(status='published')
        if exam_type:
            qs = qs.filter(exam_type=exam_type)
        if mock_type:
            qs = qs.filter(mock_type=mock_type)
        return qs

    @staticmethod
    def get_mock_access_status(user) -> dict:
        """Foydalanuvchining mock exam quota va coin holati."""
        sub = EntitlementService.get_active_subscription(user)
        quota = MockExamService._get_or_create_quota(user, sub)

        # Coin costs
        core_cost = CoinServiceCost.objects.filter(service_code='core_mock_exam').first()
        complete_cost = CoinServiceCost.objects.filter(service_code='complete_mock_exam').first()

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        # Last attempt
        last_attempt = MockExamAttempt.objects.filter(
            user=user, status='completed'
        ).order_by('-completed_at').first()

        return {
            'subscription_active': sub is not None,
            'quota': {
                'core': {
                    'total': quota.core_mock_total if quota else 0,
                    'used': quota.core_mock_used if quota else 0,
                    'remaining': quota.core_remaining if quota else 0,
                },
                'complete': {
                    'total': quota.complete_mock_total if quota else 0,
                    'used': quota.complete_mock_used if quota else 0,
                    'remaining': quota.complete_remaining if quota else 0,
                },
            },
            'coin_costs': {
                'core_mock': core_cost.cost_coins if core_cost else 25,
                'complete_mock': complete_cost.cost_coins if complete_cost else 40,
            },
            'coin_balance': wallet_balance,
            'last_attempt': {
                'id': last_attempt.id if last_attempt else None,
                'mock_type': last_attempt.mock_type if last_attempt else None,
                'overall_band': last_attempt.result.overall_band if last_attempt and hasattr(last_attempt, 'result') else None,
                'completed_at': last_attempt.completed_at.isoformat() if last_attempt and last_attempt.completed_at else None,
            } if last_attempt else None,
        }

    @staticmethod
    def can_start_mock(user, mock_id: int) -> dict:
        """Mock boshlash mumkinmi? Quota yoki coin tekshirish."""
        try:
            mock = MockExam.objects.get(id=mock_id, status='published')
        except MockExam.DoesNotExist:
            return {'allowed': False, 'reason': 'mock_not_found'}

        # Active attempt bormi?
        active = MockExamAttempt.objects.filter(
            user=user,
            status__in=['reserved', 'in_progress', 'listening_completed', 'reading_completed', 'writing_completed', 'speaking_pending']
        ).first()
        if active:
            return {'allowed': False, 'reason': 'active_attempt_exists', 'attempt_id': active.id}

        sub = EntitlementService.get_active_subscription(user)
        quota = MockExamService._get_or_create_quota(user, sub)

        # Quota tekshirish
        if mock.mock_type == 'core' and quota and quota.core_remaining > 0:
            return {'allowed': True, 'access_source': 'subscription_quota', 'requires_coin': False}
        elif mock.mock_type == 'complete' and quota and quota.complete_remaining > 0:
            return {'allowed': True, 'access_source': 'subscription_quota', 'requires_coin': False}

        # Coin tekshirish
        service_code = 'core_mock_exam' if mock.mock_type == 'core' else 'complete_mock_exam'
        cost = CoinServiceCost.objects.filter(service_code=service_code).first()
        coin_cost = cost.cost_coins if cost else (25 if mock.mock_type == 'core' else 40)

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        if wallet_balance >= coin_cost:
            return {
                'allowed': True,
                'access_source': 'coin_purchase',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'balance_after': wallet_balance - coin_cost,
            }
        else:
            return {
                'allowed': False,
                'reason': 'insufficient_resources',
                'requires_coin': True,
                'required_coin': coin_cost,
                'current_balance': wallet_balance,
                'message': f'Balansingiz yetarli emas. {coin_cost} coin kerak.',
            }

    @staticmethod
    @transaction.atomic
    def start_mock(user, mock_id: int, access_source: str = 'subscription_quota', idempotency_key: str = None) -> MockExamAttempt:
        """Mock imtihonni boshlash — quota yoki coin yechish."""
        mock = MockExam.objects.get(id=mock_id, status='published')

        # Idempotency check
        if idempotency_key:
            existing = MockExamAttempt.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return existing

        sub = EntitlementService.get_active_subscription(user)
        quota = MockExamService._get_or_create_quota(user, sub)
        coin_tx_id = None

        if access_source == 'subscription_quota':
            # Quota yechish
            if mock.mock_type == 'core':
                if not quota or quota.core_remaining <= 0:
                    raise ValueError("Core Mock quota tugagan")
                quota.core_mock_used += 1
                quota.save(update_fields=['core_mock_used', 'updated_at'])
            else:
                if not quota or quota.complete_remaining <= 0:
                    raise ValueError("Complete Mock quota tugagan")
                quota.complete_mock_used += 1
                quota.save(update_fields=['complete_mock_used', 'updated_at'])

        elif access_source == 'coin_purchase':
            # Coin yechish
            service_code = 'core_mock_exam' if mock.mock_type == 'core' else 'complete_mock_exam'
            cost = CoinServiceCost.objects.filter(service_code=service_code).first()
            coin_cost = cost.cost_coins if cost else (25 if mock.mock_type == 'core' else 40)

            wallet = WalletService.change_balance(
                user=user,
                amount=-coin_cost,
                tx_type='writing_evaluation',  # reuse existing type
                description=f"{'Core' if mock.mock_type == 'core' else 'Complete'} Mock Exam",
                related_object_type='mock_exam',
            )
            coin_tx_id = str(wallet.id)

        # Attempt yaratish
        now = timezone.now()
        attempt = MockExamAttempt.objects.create(
            user=user,
            mock_exam=mock,
            exam_type=mock.exam_type,
            mock_type=mock.mock_type,
            access_source=access_source,
            coin_transaction_id=coin_tx_id,
            status='in_progress',
            started_at=now,
            expires_at=now + timedelta(hours=4),  # 4 soat ichida tugatish kerak
            current_section='listening',
            idempotency_key=idempotency_key or str(uuid.uuid4()),
        )

        return attempt

    @staticmethod
    def save_answer(attempt_id: int, section_type: str, question_number: int, answer: str, is_flagged: bool = False):
        """Javobni saqlash (auto-save)."""
        attempt = MockExamAttempt.objects.get(id=attempt_id)
        MockExamAnswer.objects.update_or_create(
            attempt=attempt,
            section_type=section_type,
            question_number=question_number,
            defaults={
                'answer': answer,
                'is_flagged': is_flagged,
            }
        )

    @staticmethod
    def save_writing_draft(attempt_id: int, task_type: str, content: str):
        """Writing draft saqlash (auto-save)."""
        attempt = MockExamAttempt.objects.get(id=attempt_id)
        word_count = len(content.split()) if content else 0
        MockWritingSubmission.objects.update_or_create(
            attempt=attempt,
            task_type=task_type,
            defaults={
                'content': content,
                'word_count': word_count,
            }
        )

    @staticmethod
    def complete_section(attempt_id: int, section_type: str):
        """Bo'limni yakunlash."""
        attempt = MockExamAttempt.objects.get(id=attempt_id)
        now = timezone.now()

        if section_type == 'listening':
            attempt.listening_completed_at = now
            attempt.current_section = 'reading'
            attempt.status = 'listening_completed'
        elif section_type == 'reading':
            attempt.reading_completed_at = now
            attempt.current_section = 'writing'
            attempt.status = 'reading_completed'
        elif section_type == 'writing':
            attempt.writing_completed_at = now
            if attempt.mock_type == 'complete':
                attempt.current_section = 'speaking'
                attempt.status = 'speaking_pending'
            else:
                attempt.status = 'processing'
                attempt.completed_at = now
        elif section_type == 'speaking':
            attempt.speaking_completed_at = now
            attempt.status = 'processing'
            attempt.completed_at = now

        attempt.save()
        return attempt

    @staticmethod
    def submit_mock(attempt_id: int):
        """Mock imtihonni yakunlash va natijalarni hisoblash."""
        attempt = MockExamAttempt.objects.get(id=attempt_id)
        attempt.status = 'processing'
        attempt.completed_at = timezone.now()
        attempt.save()

        # Natijalarni hisoblash (hozircha placeholder)
        result = MockExamResult.objects.create(
            attempt=attempt,
            listening_band=0,
            reading_band=0,
            writing_band=0,
            speaking_band=0 if attempt.mock_type == 'complete' else None,
            overall_band=0,
            recommendations=[],
        )

        attempt.status = 'completed'
        attempt.save()
        return result

    @staticmethod
    def get_attempt_result(attempt_id: int):
        """Attempt natijasini olish."""
        try:
            return MockExamResult.objects.get(attempt_id=attempt_id)
        except MockExamResult.DoesNotExist:
            return None

    @staticmethod
    def _get_or_create_quota(user, subscription) -> MockExamQuota | None:
        """Foydalanuvchining joriy quota'sini olish yoki yaratish."""
        if not subscription:
            return None

        now = timezone.now()
        quota = MockExamQuota.objects.filter(
            user=user,
            subscription=subscription,
            period_start__lte=now,
            period_end__gte=now,
        ).first()

        if not quota:
            plan = subscription.plan
            # Plan'ga qarab quota yaratish
            core_total = 0
            complete_total = 0

            if plan:
                if plan.code == 'weekly':
                    core_total = 1
                    complete_total = 0
                elif plan.code == 'monthly':
                    core_total = 2
                    complete_total = 1

            quota = MockExamQuota.objects.create(
                user=user,
                subscription=subscription,
                core_mock_total=core_total,
                complete_mock_total=complete_total,
                period_start=subscription.start_at,
                period_end=subscription.end_at,
            )

        return quota
