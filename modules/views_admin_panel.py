"""
Admin Panel uchun API endpointlar.
Users boshqaruvi, to'lovlar tasdiqlash, loglar, coin operatsiyalari.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta

from accounts.permissions import IsAdminUser
from accounts.models import UserProfile
from subscriptions.models import (
    SubscriptionPlan, UserSubscription, CoinWallet,
    CoinTransaction, CoinPack, Payment
)
from subscriptions.services import WalletService, SubscriptionService
from attempts.models import UserDailyUsage

User = get_user_model()


# =====================================================
# USERS MANAGEMENT
# =====================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    """Admin panel uchun foydalanuvchilar ro'yxati"""
    try:
        search = request.GET.get('search', '')
        role = request.GET.get('role', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        users = User.objects.all().order_by('-date_joined')

        if search:
            users = users.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        if role:
            users = users.filter(role=role)

        total = users.count()
        offset = (page - 1) * limit
        users = users[offset:offset + limit]

        results = []
        for user in users:
            # Wallet balance
            wallet_balance = 0
            try:
                wallet = CoinWallet.objects.get(user=user)
                wallet_balance = wallet.balance
            except CoinWallet.DoesNotExist:
                pass

            # Active subscription
            active_sub = UserSubscription.objects.filter(
                user=user, is_active=True,
                start_at__lte=timezone.now(),
                end_at__gte=timezone.now()
            ).first()

            results.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.username,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.date_joined.isoformat(),
                'last_active_at': user.last_login.isoformat() if user.last_login else None,
                'user_coins': {
                    'balance': wallet_balance,
                },
                'user_subscriptions': [{
                    'plan_type': active_sub.plan.code if active_sub and active_sub.plan else None,
                    'status': 'active' if active_sub else 'none',
                    'expires_at': active_sub.end_at.isoformat() if active_sub else None,
                }] if active_sub else [],
            })

        return Response({
            'success': True,
            'data': results,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_detail(request, user_id):
    """Bitta foydalanuvchi haqida to'liq ma'lumot"""
    try:
        user = User.objects.get(id=user_id)

        wallet_balance = 0
        try:
            wallet = CoinWallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except CoinWallet.DoesNotExist:
            pass

        active_sub = UserSubscription.objects.filter(
            user=user, is_active=True,
            start_at__lte=timezone.now(),
            end_at__gte=timezone.now()
        ).first()

        profile = None
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            pass

        data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.date_joined.isoformat(),
            'last_active_at': user.last_login.isoformat() if user.last_login else None,
            'target_band_score': profile.target_band_score if profile else None,
            'user_coins': {
                'balance': wallet_balance,
            },
            'user_subscriptions': [{
                'plan_type': active_sub.plan.code if active_sub and active_sub.plan else None,
                'status': 'active',
                'started_at': active_sub.start_at.isoformat() if active_sub else None,
                'expires_at': active_sub.end_at.isoformat() if active_sub else None,
            }] if active_sub else [],
        }

        return Response({'success': True, 'data': data})

    except User.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_adjust_coins(request):
    """Admin tomonidan foydalanuvchiga coin qo'shish/yechish"""
    try:
        user_id = request.data.get('user_id')
        amount = int(request.data.get('amount', 0))
        description = request.data.get('description', 'Admin tomonidan o\'zgartirildi')

        user = User.objects.get(id=user_id)
        wallet = WalletService.change_balance(
            user=user,
            amount=amount,
            tx_type='manual_adjustment',
            description=description,
        )

        return Response({
            'success': True,
            'data': {
                'user_id': str(user.id),
                'new_balance': wallet.balance,
                'amount': amount,
            }
        })

    except User.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_subscription(request):
    """Admin tomonidan foydalanuvchiga obuna berish/o'chirish"""
    try:
        user_id = request.data.get('user_id')
        plan_type = request.data.get('plan_type')
        sub_status = request.data.get('status', 'active')

        user = User.objects.get(id=user_id)

        if sub_status == 'active' and plan_type:
            plan = SubscriptionPlan.objects.get(code=plan_type)
            sub = SubscriptionService.activate_subscription(user=user, plan=plan)
            return Response({
                'success': True,
                'data': {
                    'user_id': str(user.id),
                    'plan_type': plan.code,
                    'status': 'active',
                    'expires_at': sub.end_at.isoformat(),
                }
            })
        else:
            # Deactivate
            UserSubscription.objects.filter(user=user, is_active=True).update(is_active=False)
            return Response({
                'success': True,
                'data': {
                    'user_id': str(user.id),
                    'plan_type': plan_type,
                    'status': 'cancelled',
                }
            })

    except User.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)
    except SubscriptionPlan.DoesNotExist:
        return Response({'success': False, 'error': 'Plan not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# =====================================================
# PAYMENTS MANAGEMENT
# =====================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_payments_list(request):
    """Admin panel uchun to'lovlar ro'yxati"""
    try:
        payment_status = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        payments = Payment.objects.all().select_related('user', 'plan', 'coin_pack').order_by('-created_at')

        # Status counts
        pending_count = Payment.objects.filter(status='pending').count()
        approved_count = Payment.objects.filter(status='paid').count()
        rejected_count = Payment.objects.filter(status='failed').count()

        if payment_status:
            # Map frontend status names to backend
            status_map = {'pending': 'pending', 'approved': 'paid', 'rejected': 'failed'}
            backend_status = status_map.get(payment_status, payment_status)
            payments = payments.filter(status=backend_status)

        total = payments.count()
        offset = (page - 1) * limit
        payments = payments[offset:offset + limit]

        results = []
        for payment in payments:
            # Build receipt URL
            receipt_url = None
            if payment.receipt_image:
                receipt_url = request.build_absolute_uri(payment.receipt_image.url)

            # Map status for frontend
            frontend_status = payment.status
            if payment.status == 'paid':
                frontend_status = 'approved'
            elif payment.status == 'failed':
                frontend_status = 'rejected'

            results.append({
                'id': str(payment.id),
                'user_id': str(payment.user.id),
                'amount': payment.amount_uzs,
                'currency': 'UZS',
                'payment_type': 'subscription' if payment.plan else 'coin_purchase',
                'plan_type': payment.plan.code if payment.plan else None,
                'coins_requested': payment.coin_pack.coins if payment.coin_pack else None,
                'status': frontend_status,
                'receipt_image_url': receipt_url,
                'admin_note': payment.extra_data.get('reject_reason', '') if payment.extra_data else '',
                'created_at': payment.created_at.isoformat(),
                'profiles': {
                    'email': payment.user.email,
                    'full_name': payment.user.get_full_name() or payment.user.username,
                },
            })

        return Response({
            'success': True,
            'data': results,
            'counts': {
                'pending': pending_count,
                'approved': approved_count,
                'rejected': rejected_count,
                'total': pending_count + approved_count + rejected_count,
            },
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
            }
        })

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_approve_payment(request):
    """To'lovni tasdiqlash"""
    try:
        payment_id = request.data.get('payment_id')
        payment = Payment.objects.get(id=payment_id)

        if payment.status == Payment.STATUS_PAID:
            return Response({'success': False, 'error': 'Already approved'}, status=400)

        from subscriptions.services import PaymentService
        payment = PaymentService.handle_payment_callback(
            payment=payment,
            status=Payment.STATUS_PAID,
            provider_payment_id=f'admin_approved_{request.user.id}',
        )

        return Response({
            'success': True,
            'data': {
                'payment_id': str(payment.id),
                'status': payment.status,
            }
        })

    except Payment.DoesNotExist:
        return Response({'success': False, 'error': 'Payment not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_reject_payment(request):
    """To'lovni rad etish"""
    try:
        payment_id = request.data.get('payment_id')
        reason = request.data.get('reason', '')
        payment = Payment.objects.get(id=payment_id)

        payment.status = Payment.STATUS_FAILED
        payment.extra_data = payment.extra_data or {}
        payment.extra_data['reject_reason'] = reason
        payment.extra_data['rejected_by'] = request.user.id
        payment.save()

        return Response({
            'success': True,
            'data': {
                'payment_id': str(payment.id),
                'status': payment.status,
                'reason': reason,
            }
        })

    except Payment.DoesNotExist:
        return Response({'success': False, 'error': 'Payment not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# =====================================================
# LOGS & TRANSACTIONS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_logs(request):
    """Admin harakatlari logi (hozircha coin transactions asosida)"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        # Hozircha admin tomonidan qilingan coin transactionlarni log sifatida ko'rsatamiz
        transactions = CoinTransaction.objects.filter(
            type='manual_adjustment'
        ).select_related('user').order_by('-created_at')

        total = transactions.count()
        offset = (page - 1) * limit
        transactions = transactions[offset:offset + limit]

        results = []
        for tx in transactions:
            results.append({
                'id': str(tx.id),
                'admin_id': '',
                'action': 'coin_adjustment',
                'target_type': 'user',
                'target_id': str(tx.user.id) if tx.user else '',
                'metadata': {
                    'amount': tx.amount,
                    'description': tx.description,
                },
                'created_at': tx.created_at.isoformat(),
                'profiles': {
                    'email': tx.user.email if tx.user else '',
                    'full_name': tx.user.get_full_name() if tx.user else '',
                },
            })

        return Response({
            'success': True,
            'data': results,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
            }
        })

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_coin_transactions(request):
    """Barcha coin transactionlar"""
    try:
        user_id = request.GET.get('user_id', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        transactions = CoinTransaction.objects.all().select_related('user').order_by('-created_at')

        if user_id:
            transactions = transactions.filter(user_id=user_id)

        total = transactions.count()
        offset = (page - 1) * limit
        transactions = transactions[offset:offset + limit]

        results = []
        for tx in transactions:
            results.append({
                'id': str(tx.id),
                'user_id': str(tx.user.id) if tx.user else '',
                'amount': tx.amount,
                'transaction_type': tx.type or 'unknown',
                'description': tx.description,
                'created_at': tx.created_at.isoformat(),
                'profiles': {
                    'email': tx.user.email if tx.user else '',
                    'full_name': tx.user.get_full_name() if tx.user else '',
                },
            })

        return Response({
            'success': True,
            'data': results,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
            }
        })

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
