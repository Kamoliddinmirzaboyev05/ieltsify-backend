from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Q, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth import get_user_model

from .models import ListeningTest, ReadingPassage, WritingTask, SmartArticle, ListeningMaterial, VocabularyWord
from attempts.models import UserDailyUsage
from subscriptions.models import SubscriptionPlan, UserSubscription, CoinWallet, CoinTransaction, Payment

User = get_user_model()


@swagger_auto_schema(
    method='GET',
    operation_description="Admin Dashboard uchun barcha statistikalar",
    responses={
        200: openapi.Response(
            description="Admin dashboard ma'lumotlari muvaffaqiyatli olindi",
            examples={
                'application/json': {
                    'success': True,
                    'data': {
                        'overview': {
                            'total_users': 1250,
                            'active_users': 890,
                            'premium_users': 156,
                            'total_revenue': 12500000,
                            'current_month_revenue': 2100000
                        },
                        'user_statistics': {
                            'new_users_today': 12,
                            'new_users_this_week': 68,
                            'new_users_this_month': 245,
                            'user_growth_rate': 15.5,
                            'most_active_users': [
                                {'email': 'user1@example.com', 'activity_score': 95},
                                {'email': 'user2@example.com', 'activity_score': 87}
                            ]
                        },
                        'subscription_statistics': {
                            'total_subscriptions': 156,
                            'active_subscriptions': 142,
                            'expired_subscriptions': 14,
                            'subscriptions_by_plan': {
                                'free': 1094,
                                'basic_weekly': 89,
                                'basic_monthly': 67
                            },
                            'monthly_recurring_revenue': 1890000,
                            'subscription_conversion_rate': 12.5
                        },
                        'content_statistics': {
                            'listening_tests': 45,
                            'reading_passages': 38,
                            'writing_tasks': 52,
                            'smart_articles': 125,
                            'listening_materials': 67,
                            'vocabulary_words': 2500
                        },
                        'usage_statistics': {
                            'total_daily_usages': 15680,
                            'active_users_today': 234,
                            'average_session_duration': 25.5,
                            'most_used_features': {
                                'vocabulary_learning': 45,
                                'reading_tests': 32,
                                'listening_tests': 28,
                                'writing_evaluations': 18,
                                'speaking_mocks': 12
                            }
                        },
                        'financial_statistics': {
                            'total_payments': 892,
                            'successful_payments': 856,
                            'failed_payments': 36,
                            'total_revenue': 12500000,
                            'monthly_revenue': 2100000,
                            'average_transaction_value': 14600,
                            'revenue_by_payment_type': {
                                'subscriptions': 18900000,
                                'coin_purchases': 3600000
                            }
                        },
                        'coin_statistics': {
                            'total_coins_distributed': 156000,
                            'total_coins_spent': 89000,
                            'active_wallets': 890,
                            'total_wallet_balance': 67000,
                            'coins_by_transaction_type': {
                                'subscription_bonus': 125000,
                                'coin_shop_purchase': 45000,
                                'writing_evaluation': 28000,
                                'speaking_mock': 16000
                            }
                        },
                        'recent_activities': [
                            {
                                'type': 'new_user',
                                'description': 'New user registered: user@example.com',
                                'timestamp': '2024-02-20T10:30:00Z'
                            },
                            {
                                'type': 'subscription',
                                'description': 'User upgraded to Basic Monthly',
                                'timestamp': '2024-02-20T09:15:00Z'
                            }
                        ],
                        'top_performers': {
                            'highest_band_scores': [
                                {'email': 'user1@example.com', 'overall_band': 8.5},
                                {'email': 'user2@example.com', 'overall_band': 8.2}
                            ],
                            'most_consistent': [
                                {'email': 'user3@example.com', 'streak_days': 45},
                                {'email': 'user4@example.com', 'streak_days': 38}
                            ]
                        }
                    }
                }
            }
        ),
        401: "Unauthorized",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error"
    },
    tags=['Admin Dashboard']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard_statistics(request):
    """
    Admin Dashboard uchun barcha statistikalar
    Faqat admin rolidagi foydalanuvchilar uchun
    """
    try:
        # Admin rolini tekshirish
        if not request.user.is_admin_role():
            return Response({
                'success': False,
                'error': 'Admin access required',
                'message': 'Bu endpoint faqat adminlar uchun'
            }, status=status.HTTP_403_FORBIDDEN)
        
        now = timezone.now()
        
        # 1. Overview statistikasi
        overview = get_overview_statistics(now)
        
        # 2. User statistikasi
        user_statistics = get_user_statistics(now)
        
        # 3. Subscription statistikasi
        subscription_statistics = get_subscription_statistics(now)
        
        # 4. Content statistikasi
        content_statistics = get_content_statistics()
        
        # 5. Usage statistikasi
        usage_statistics = get_usage_statistics()
        
        # 6. Financial statistikasi
        financial_statistics = get_financial_statistics(now)
        
        # 7. Coin statistikasi
        coin_statistics = get_coin_statistics()
        
        # 8. Recent activities
        recent_activities = get_recent_activities()
        
        # 9. Top performers
        top_performers = get_top_performers()
        
        data = {
            'overview': overview,
            'user_statistics': user_statistics,
            'subscription_statistics': subscription_statistics,
            'content_statistics': content_statistics,
            'usage_statistics': usage_statistics,
            'financial_statistics': financial_statistics,
            'coin_statistics': coin_statistics,
            'recent_activities': recent_activities,
            'top_performers': top_performers
        }
        
        return Response({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f"{type(e).__name__}: {str(e)}",
            'message': "Admin dashboard ma'lumotlarini olishda xatolik yuz berdi"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_overview_statistics(now):
    """Umumiy ko'rish statistikasi"""
    total_users = User.objects.count()
    active_users = UserDailyUsage.objects.filter(
        date__gte=now - timedelta(days=7)
    ).values('user').distinct().count()
    
    # Premium users (active subscriptions)
    premium_users = UserSubscription.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now
    ).count()
    
    # Total revenue
    total_revenue = Payment.objects.filter(
        status='paid'
    ).aggregate(total=Sum('amount_uzs'))['total'] or 0
    
    # Current month revenue
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_revenue = Payment.objects.filter(
        status='paid',
        created_at__gte=current_month_start
    ).aggregate(total=Sum('amount_uzs'))['total'] or 0
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'premium_users': premium_users,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue
    }


def get_user_statistics(now):
    """Foydalanuvchi statistikasi"""
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_this_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_this_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # User growth rate (monthly)
    last_month_users = User.objects.filter(
        date_joined__date__gte=month_ago - timedelta(days=30),
        date_joined__date__lt=month_ago
    ).count()
    
    user_growth_rate = ((new_users_this_month - last_month_users) / max(last_month_users, 1)) * 100
    
    # Most active users (last 30 days)
    most_active_users = UserDailyUsage.objects.filter(
        date__gte=month_ago
    ).values('user__email').annotate(
        activity_score=Sum('vocab_learned_count') + Sum('writing_evaluation_count') + 
                     Sum('speaking_mock_count') + Sum('reading_attempt_count') + 
                     Sum('listening_attempt_count')
    ).order_by('-activity_score')[:5]
    
    return {
        'new_users_today': new_users_today,
        'new_users_this_week': new_users_this_week,
        'new_users_this_month': new_users_this_month,
        'user_growth_rate': round(user_growth_rate, 1),
        'most_active_users': [
            {
                'email': user['user__email'],
                'activity_score': user['activity_score']
            }
            for user in most_active_users
        ]
    }


def get_subscription_statistics(now):
    """Obuna statistikasi"""
    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now
    ).count()
    
    expired_subscriptions = total_subscriptions - active_subscriptions
    
    # Subscriptions by plan
    subscriptions_by_plan = {}
    for plan in SubscriptionPlan.objects.all():
        count = UserSubscription.objects.filter(
            plan=plan,
            is_active=True,
            start_at__lte=now,
            end_at__gte=now
        ).count()
        subscriptions_by_plan[plan.code] = count
    
    # Free users
    free_users = User.objects.count() - active_subscriptions
    subscriptions_by_plan['free'] = free_users
    
    # Monthly recurring revenue
    monthly_recurring_revenue = UserSubscription.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now,
        plan__duration_days=30
    ).aggregate(total=Sum('plan__price_uzs'))['total'] or 0
    
    # Conversion rate
    subscription_conversion_rate = (active_subscriptions / max(User.objects.count(), 1)) * 100
    
    return {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'subscriptions_by_plan': subscriptions_by_plan,
        'monthly_recurring_revenue': monthly_recurring_revenue,
        'subscription_conversion_rate': round(subscription_conversion_rate, 1)
    }


def get_content_statistics():
    """Kontent statistikasi"""
    return {
        'listening_tests': ListeningTest.objects.count(),
        'reading_passages': ReadingPassage.objects.count(),
        'writing_tasks': WritingTask.objects.count(),
        'smart_articles': SmartArticle.objects.count(),
        'listening_materials': ListeningMaterial.objects.count(),
        'vocabulary_words': VocabularyWord.objects.count()
    }


def get_usage_statistics():
    """Foydalanish statistikasi"""
    total_daily_usages = UserDailyUsage.objects.count()
    today = timezone.now().date()
    active_users_today = UserDailyUsage.objects.filter(date=today).count()
    
    # Average session duration (yaratilgan ma'lumot asosida)
    average_session_duration = 25.5  # Bu real ma'lumotlardan hisoblanishi kerak
    
    # Most used features
    most_used_features = UserDailyUsage.objects.aggregate(
        vocabulary_learning=Sum('vocab_learned_count'),
        reading_tests=Sum('reading_attempt_count'),
        listening_tests=Sum('listening_attempt_count'),
        writing_evaluations=Sum('writing_evaluation_count'),
        speaking_mocks=Sum('speaking_mock_count')
    )
    
    return {
        'total_daily_usages': total_daily_usages,
        'active_users_today': active_users_today,
        'average_session_duration': average_session_duration,
        'most_used_features': {
            'vocabulary_learning': most_used_features['vocabulary_learning'] or 0,
            'reading_tests': most_used_features['reading_tests'] or 0,
            'listening_tests': most_used_features['listening_tests'] or 0,
            'writing_evaluations': most_used_features['writing_evaluations'] or 0,
            'speaking_mocks': most_used_features['speaking_mocks'] or 0
        }
    }


def get_financial_statistics(now):
    """Moliyaviy statistikasi"""
    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(status='paid').count()
    failed_payments = Payment.objects.filter(status='failed').count()
    
    total_revenue = Payment.objects.filter(status='paid').aggregate(
        total=Sum('amount_uzs')
    )['total'] or 0
    
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Payment.objects.filter(
        status='paid',
        created_at__gte=current_month_start
    ).aggregate(total=Sum('amount_uzs'))['total'] or 0
    
    average_transaction_value = total_revenue / max(successful_payments, 1)
    
    # Revenue by payment type
    subscription_revenue = Payment.objects.filter(
        status='paid',
        plan__isnull=False
    ).aggregate(total=Sum('amount_uzs'))['total'] or 0
    
    coin_revenue = Payment.objects.filter(
        status='paid',
        coin_pack__isnull=False
    ).aggregate(total=Sum('amount_uzs'))['total'] or 0
    
    return {
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'failed_payments': failed_payments,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'average_transaction_value': round(average_transaction_value),
        'revenue_by_payment_type': {
            'subscriptions': subscription_revenue,
            'coin_purchases': coin_revenue
        }
    }


def get_coin_statistics():
    """Tanga statistikasi"""
    total_coins_distributed = CoinTransaction.objects.filter(
        amount__gt=0
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_coins_spent = CoinTransaction.objects.filter(
        amount__lt=0
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    active_wallets = CoinWallet.objects.count()
    total_wallet_balance = CoinWallet.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    # Coins by transaction type
    coins_by_type = {}
    for transaction_type, _ in CoinTransaction.TYPE_CHOICES:
        total = CoinTransaction.objects.filter(
            type=transaction_type
        ).aggregate(total=Sum('amount'))['total'] or 0
        coins_by_type[transaction_type] = abs(total)
    
    return {
        'total_coins_distributed': total_coins_distributed,
        'total_coins_spent': abs(total_coins_spent),
        'active_wallets': active_wallets,
        'total_wallet_balance': total_wallet_balance,
        'coins_by_transaction_type': coins_by_type
    }


def get_recent_activities():
    """So'nggi faoliyatlar"""
    activities = []
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:3]
    for user in recent_users:
        activities.append({
            'type': 'new_user',
            'description': f'New user registered: {user.email}',
            'timestamp': user.date_joined.isoformat()
        })
    
    # Recent subscriptions
    recent_subscriptions = UserSubscription.objects.order_by('-created_at')[:3]
    for sub in recent_subscriptions:
        activities.append({
            'type': 'subscription',
            'description': f'User subscribed to {sub.plan.name if sub.plan else "Unknown"}',
            'timestamp': sub.created_at.isoformat()
        })
    
    # Recent payments
    recent_payments = Payment.objects.filter(status='paid').order_by('-created_at')[:3]
    for payment in recent_payments:
        activities.append({
            'type': 'payment',
            'description': f'Payment received: {payment.amount_uzs} UZS',
            'timestamp': payment.created_at.isoformat()
        })
    
    # Sort by timestamp and return latest 10
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:10]


def get_top_performers():
    """Eng yaxshi natijalari"""
    from accounts.models import UserProfile as UserProfileModel
    # Highest band scores
    top_scores = []
    try:
        profiles = UserProfileModel.objects.select_related('user').order_by('-listening_score')[:5]
        for profile in profiles:
            overall_band = (profile.listening_score + profile.reading_score + 
                            profile.writing_score + profile.speaking_score) / 4
            top_scores.append({
                'email': profile.user.email,
                'overall_band': round(overall_band, 1)
            })
    except Exception:
        pass
    
    # Most consistent users (based on daily usage streak)
    most_consistent = []
    users_with_streak = []
    for user in User.objects.all()[:10]:  # Limit for performance
        streak = calculate_user_streak(user)
        users_with_streak.append({
            'email': user.email,
            'streak_days': streak
        })
    
    users_with_streak.sort(key=lambda x: x['streak_days'], reverse=True)
    most_consistent = users_with_streak[:5]
    
    return {
        'highest_band_scores': top_scores,
        'most_consistent': most_consistent
    }


def calculate_user_streak(user):
    """Foydalanuvchi streakini hisoblash"""
    daily_usages = UserDailyUsage.objects.filter(user=user).order_by('-date')
    if not daily_usages.exists():
        return 0
    
    streak = 0
    current_date = timezone.now().date()
    
    for usage in daily_usages:
        if usage.date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif usage.date == current_date + timedelta(days=1):
            continue
        else:
            break
    
    return streak
