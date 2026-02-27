from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    SubscriptionPlan,
    UserSubscription,
    CoinWallet,
    CoinTransaction,
    CoinPack,
    Payment,
)

User = get_user_model()


class WalletService:
    """
    Coin balansini xavfsiz boshqarish uchun service.
    """

    @staticmethod
    def get_or_create_wallet(user: User) -> CoinWallet:
        wallet, _ = CoinWallet.objects.get_or_create(user=user)
        return wallet

    @staticmethod
    def change_balance(
            user: User,
            amount: int,
            tx_type: str | None = None,
            description: str | None = None,
            related_object_id: str | None = None,
            related_object_type: str | None = None,
    ) -> CoinWallet:
        """
        Balansni o'zgartirish (depozit yoki yechish).
        amount manfiy bo'lishi ham mumkin.
        """
        with transaction.atomic():
            wallet = WalletService.get_or_create_wallet(user)

            new_balance = wallet.balance + amount
            if new_balance < 0:
                raise ValueError("Yetarli coin mavjud emas")

            wallet.balance = new_balance
            wallet.save(update_fields=["balance", "updated_at"])

            CoinTransaction.objects.create(
                user=user,
                wallet=wallet,
                amount=amount,
                type=tx_type,
                description=description,
                related_object_id=related_object_id,
                related_object_type=related_object_type,
            )

            return wallet


class SubscriptionService:
    """
    Obuna bilan ishlash logikasi.
    """

    @staticmethod
    def get_active_subscription(user: User) -> UserSubscription | None:
        now = timezone.now()
        return (
            UserSubscription.objects.filter(
                user=user,
                is_active=True,
                start_at__lte=now,
                end_at__gte=now,
            )
            .select_related("plan")
            .first()
        )

    @staticmethod
    def activate_subscription(user: User, plan: SubscriptionPlan) -> UserSubscription:
        """
        To'lov tasdiqlanganda chaqiriladi:
        - Eski aktiv obunalarni o'chiradi
        - Yangi obunani yaratadi
        - Plan bo'yicha coin beradi
        """
        now = timezone.now()
        with transaction.atomic():
            # Eski aktivlarni o'chirish
            UserSubscription.objects.filter(user=user, is_active=True).update(
                is_active=False
            )

            sub = UserSubscription.objects.create(
                user=user,
                plan=plan,
                start_at=now,
                end_at=now + timedelta(days=plan.duration_days),
                is_active=True,
            )

            # Plan bo'yicha coin bonus
            if plan.included_coins > 0:
                WalletService.change_balance(
                    user=user,
                    amount=plan.included_coins,
                    tx_type="subscription_bonus",
                    description=f"{plan.name} obunasi uchun bonus coin",
                )

            return sub


class PaymentService:
    """
    Subscription va CoinPack uchun Payment yaratish va callbackni qayta ishlash.
    """

    @staticmethod
    def create_subscription_payment(
            user: User,
            plan: SubscriptionPlan,
            provider: str,
    ) -> Payment:
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount_uzs=plan.price_uzs,
            provider=provider,
            status=Payment.STATUS_PENDING,
        )
        return payment

    @staticmethod
    def create_coin_pack_payment(
            user: User,
            coin_pack: CoinPack,
            provider: str,
    ) -> Payment:
        payment = Payment.objects.create(
            user=user,
            coin_pack=coin_pack,
            amount_uzs=coin_pack.price_uzs,
            provider=provider,
            status=Payment.STATUS_PENDING,
        )
        return payment

    @staticmethod
    def handle_payment_callback(
            payment: Payment,
            status: str,
            provider_payment_id: str | None = None,
            extra_data: dict | None = None,
    ) -> Payment:
        """
        Click/Payme callbackdan keyin to'lovni yakunlash.
        """
        if payment.status == Payment.STATUS_PAID:
            # Idempotentlik: allaqachon to'langan bo'lsa, qayta ishlamaymiz
            return payment

        with transaction.atomic():
            payment.provider_payment_id = (
                    provider_payment_id or payment.provider_payment_id
            )
            payment.status = status
            if extra_data:
                payment.extra_data = extra_data
            payment.save(update_fields=["provider_payment_id", "status", "extra_data", "updated_at"])

            if status == Payment.STATUS_PAID:
                # Agar bu subscription bo'lsa
                if payment.plan:
                    SubscriptionService.activate_subscription(
                        user=payment.user,
                        plan=payment.plan,
                    )

                # Agar bu coin pack bo'lsa
                if payment.coin_pack:
                    WalletService.change_balance(
                        user=payment.user,
                        amount=payment.coin_pack.coins,
                        tx_type="coin_shop_purchase",
                        description=f"{payment.coin_pack.name} sotib olindi",
                    )

        return payment


class CoinConsumptionService:
    """
    AI xizmatlari uchun tanga yechish logikasi.
    Bu service'ni keyinchalik writing/speaking endpointlarida ishlatasiz.
    """

    WRITING_EVAL_COST = 10
    SPEAKING_MOCK_COST = 15
    SMART_ARTICLE_TRANSLATION_COST = 1  # 1 coin = 5 ta so'z tarjimasi kabi

    @staticmethod
    def charge_for_writing_evaluation(user: User, related_object_id: str | None = None):
        return WalletService.change_balance(
            user=user,
            amount=-CoinConsumptionService.WRITING_EVAL_COST,
            tx_type="writing_evaluation",
            description="AI Writing Evaluation",
            related_object_id=related_object_id,
            related_object_type="writing_attempt",
        )

    @staticmethod
    def charge_for_speaking_mock(user: User, related_object_id: str | None = None):
        return WalletService.change_balance(
            user=user,
            amount=-CoinConsumptionService.SPEAKING_MOCK_COST,
            tx_type="speaking_mock",
            description="AI Speaking Mock",
            related_object_id=related_object_id,
            related_object_type="speaking_attempt",
        )

    @staticmethod
    def charge_for_smart_article_translation(
            user: User,
            related_object_id: str | None = None,
    ):
        return WalletService.change_balance(
            user=user,
            amount=-CoinConsumptionService.SMART_ARTICLE_TRANSLATION_COST,
            tx_type="smart_article_translation",
            description="Smart Article translation",
            related_object_id=related_object_id,
            related_object_type="smart_article",
        )
