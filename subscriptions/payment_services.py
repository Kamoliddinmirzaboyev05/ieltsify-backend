import hashlib
import hmac
import json
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings
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


class PaymentGatewayService:
    """Click va Payme bilan ishlash uchun umumiy service"""
    
    @staticmethod
    def generate_click_payment_url(payment: Payment) -> str:
        """Click to'lov URL ni generatsiya qilish"""
        params = {
            'service_id': settings.CLICK_SERVICE_ID,
            'merchant_trans_id': payment.id,
            'amount': payment.amount_uzs,
            'return_url': f'{settings.FRONTEND_URL}/payment/success?payment_id={payment.id}',
            'callback_url': settings.CLICK_CALLBACK_URL,
        }
        
        # Click uchun imzo yaratish (agar kerak bo'lsa)
        if settings.CLICK_SECRET_KEY:
            params['sign'] = PaymentGatewayService._generate_click_sign(params)
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{settings.CLICK_PAYMENT_URL}?{query_string}"
    
    @staticmethod
    def generate_payme_payment_url(payment: Payment) -> str:
        """Payme to'lov URL ni generatsiya qilish"""
        params = {
            'service_id': settings.PAYME_SERVICE_ID,
            'merchant_trans_id': payment.id,
            'amount': payment.amount_uzs * 100,  # Payme tiyinlarda ishlaydi
            'return_url': f'{settings.FRONTEND_URL}/payment/success?payment_id={payment.id}',
            'callback_url': settings.PAYME_CALLBACK_URL,
        }
        
        # Payme uchun imzo yaratish (agar kerak bo'lsa)
        if settings.PAYME_SECRET_KEY:
            params['sign'] = PaymentGatewayService._generate_payme_sign(params)
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{settings.PAYME_PAYMENT_URL}?{query_string}"
    
    @staticmethod
    def _generate_click_sign(params: dict) -> str:
        """Click uchun imzo generatsiyasi"""
        # Click imzo algoritmi (hujjatlar asosida)
        secret_key = settings.CLICK_SECRET_KEY
        sign_string = f"{params['service_id']}{params['merchant_trans_id']}{params['amount']}{secret_key}"
        return hashlib.md5(sign_string.encode()).hexdigest()
    
    @staticmethod
    def _generate_payme_sign(params: dict) -> str:
        """Payme uchun imzo generatsiyasi"""
        # Payme imzo algoritmi (hujjatlar asosida)
        secret_key = settings.PAYME_SECRET_KEY
        sign_string = f"{params['service_id']}{params['merchant_trans_id']}{params['amount']}{secret_key}"
        return hashlib.md5(sign_string.encode()).hexdigest()
    
    @staticmethod
    def verify_click_callback(data: dict) -> bool:
        """Click callback ni tekshirish"""
        if not settings.CLICK_SECRET_KEY:
            return True  # Secret key bo'lmasa, tekshirmaymiz
        
        # Click dan kelgan imzoni tekshirish
        received_sign = data.get('sign')
        if not received_sign:
            return False
        
        # Imzo generatsiya qilish
        sign_data = {
            'service_id': data.get('service_id'),
            'merchant_trans_id': data.get('merchant_trans_id'),
            'amount': data.get('amount'),
        }
        expected_sign = PaymentGatewayService._generate_click_sign(sign_data)
        
        return hmac.compare_digest(received_sign, expected_sign)
    
    @staticmethod
    def verify_payme_callback(data: dict) -> bool:
        """Payme callback ni tekshirish"""
        if not settings.PAYME_SECRET_KEY:
            return True  # Secret key bo'lmasa, tekshirmaymiz
        
        # Payme dan kelgan imzoni tekshirish
        received_sign = data.get('sign')
        if not received_sign:
            return False
        
        # Imzo generatsiya qilish
        sign_data = {
            'service_id': data.get('service_id'),
            'merchant_trans_id': data.get('merchant_trans_id'),
            'amount': data.get('amount'),
        }
        expected_sign = PaymentGatewayService._generate_payme_sign(sign_data)
        
        return hmac.compare_digest(received_sign, expected_sign)


class EnhancedPaymentService:
    """Click va Payme integratsiyasi bilan ishlaydigan payment service"""
    
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
        
        # Payment URL ni generatsiya qilish
        if provider == Payment.PROVIDER_CLICK:
            payment.payment_url = PaymentGatewayService.generate_click_payment_url(payment)
        elif provider == Payment.PROVIDER_PAYME:
            payment.payment_url = PaymentGatewayService.generate_payme_payment_url(payment)
        
        payment.save()
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
        
        # Payment URL ni generatsiya qilish
        if provider == Payment.PROVIDER_CLICK:
            payment.payment_url = PaymentGatewayService.generate_click_payment_url(payment)
        elif provider == Payment.PROVIDER_PAYME:
            payment.payment_url = PaymentGatewayService.generate_payme_payment_url(payment)
        
        payment.save()
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
                    from .services import SubscriptionService
                    SubscriptionService.activate_subscription(
                        user=payment.user,
                        plan=payment.plan,
                    )

                # Agar bu coin pack bo'lsa
                if payment.coin_pack:
                    from .services import WalletService
                    WalletService.change_balance(
                        user=payment.user,
                        amount=payment.coin_pack.coins,
                        tx_type="coin_shop_purchase",
                        description=f"{payment.coin_pack.name} sotib olindi",
                    )

        return payment


# PaymentService ni yangilash
PaymentService = EnhancedPaymentService
