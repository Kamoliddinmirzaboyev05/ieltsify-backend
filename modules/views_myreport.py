from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Q, Avg, Sum, Max
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth import get_user_model

from .models import ListeningTest, ReadingPassage, WritingTask, SmartArticle, ListeningMaterial, VocabularyWord
from attempts.models import UserDailyUsage

User = get_user_model()


@swagger_auto_schema(
    method='GET',
    operation_description="MyReport sahifasi uchun ma'lumotlar",
    responses={
        200: openapi.Response(
            description="MyReport ma'lumotlari muvaffaqiyatli olindi",
            examples={
                'application/json': {
                    'success': True,
                    'data': {
                        'user_info': {
                            'username': 'john_doe',
                            'email': 'john@example.com',
                            'full_name': 'John Doe',
                            'join_date': '2024-01-15',
                            'is_premium': True
                        },
                        'daily_statistics': {
                            'total_days_active': 25,
                            'current_streak': 7,
                            'longest_streak': 12,
                            'total_vocab_learned': 150,
                            'total_writing_evaluations': 20,
                            'total_speaking_mocks': 8,
                            'total_reading_attempts': 35,
                            'total_listening_attempts': 28
                        },
                        'recent_activity': {
                            'last_active_date': '2024-02-20',
                            'days_since_last_activity': 2,
                            'most_active_day': '2024-02-18'
                        },
                        'weekly_progress': [
                            {'date': '2024-02-14', 'vocab': 5, 'writing': 2, 'speaking': 1, 'reading': 3, 'listening': 2},
                            {'date': '2024-02-15', 'vocab': 8, 'writing': 1, 'speaking': 0, 'reading': 2, 'listening': 3},
                            {'date': '2024-02-16', 'vocab': 3, 'writing': 3, 'speaking': 1, 'reading': 1, 'listening': 2},
                            {'date': '2024-02-17', 'vocab': 0, 'writing': 0, 'speaking': 0, 'reading': 0, 'listening': 0},
                            {'date': '2024-02-18', 'vocab': 10, 'writing': 2, 'speaking': 2, 'reading': 4, 'listening': 3},
                            {'date': '2024-02-19', 'vocab': 6, 'writing': 1, 'speaking': 0, 'reading': 2, 'listening': 1},
                            {'date': '2024-02-20', 'vocab': 7, 'writing': 2, 'speaking': 1, 'reading': 3, 'listening': 2}
                        ],
                        'monthly_summary': {
                            'current_month_days': 20,
                            'current_month_vocab': 85,
                            'current_month_writing': 15,
                            'current_month_speaking': 6,
                            'current_month_reading': 25,
                            'current_month_listening': 18
                        },
                        'achievements': {
                            'vocab_master': False,
                            'writing_champion': False,
                            'speaking_star': False,
                            'reading_enthusiast': True,
                            'listening_expert': False,
                            'consistency_king': True
                        },
                        'recommendations': [
                            'Vocabulary learningni ko\'paytiring - o\'rtasida 3 kun bo\'sh',
                            'Speaking mock testlariga ko\'proq e\'tibor bering',
                            'Har kuni kamida bitta faoliyat qiling'
                        ]
                    }
                }
            }
        ),
        401: "Unauthorized",
        500: "Internal Server Error"
    },
    tags=['MyReport']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_report_data(request):
    """
    MyReport sahifasi uchun barcha ma'lumotlar
    """
    try:
        user = request.user
        now = timezone.now()
        
        # 1. Foydalanuvchi ma'lumotlari
        user_info = {
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username,
            'join_date': user.date_joined.strftime('%Y-%m-%d'),
            'is_premium': getattr(user, 'is_premium', False)
        }
        
        # 2. Kunlik statistikasi
        daily_usages = UserDailyUsage.objects.filter(user=user)
        
        # Umumiy statistika
        total_days_active = daily_usages.count()
        current_streak = calculate_current_streak(daily_usages)
        longest_streak = calculate_longest_streak(daily_usages)
        
        # Jami faoliyatlar
        total_stats = daily_usages.aggregate(
            total_vocab=Sum('vocab_learned_count'),
            total_writing=Sum('writing_evaluation_count'),
            total_speaking=Sum('speaking_mock_count'),
            total_reading=Sum('reading_attempt_count'),
            total_listening=Sum('listening_attempt_count')
        )
        
        daily_statistics = {
            'total_days_active': total_days_active,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_vocab_learned': total_stats['total_vocab'] or 0,
            'total_writing_evaluations': total_stats['total_writing'] or 0,
            'total_speaking_mocks': total_stats['total_speaking'] or 0,
            'total_reading_attempts': total_stats['total_reading'] or 0,
            'total_listening_attempts': total_stats['total_listening'] or 0
        }
        
        # 3. So'nggi faoliyat
        last_usage = daily_usages.order_by('-date').first()
        recent_activity = {
            'last_active_date': last_usage.date.strftime('%Y-%m-%d') if last_usage else None,
            'days_since_last_activity': (now.date() - last_usage.date).days if last_usage else None,
            'most_active_day': get_most_active_day(daily_usages)
        }
        
        # 4. Haftalik progress
        weekly_progress = get_weekly_progress(daily_usages)
        
        # 5. Oylik xulosa
        monthly_summary = get_monthly_summary(daily_usages, now)
        
        # 6. Yutuqlar
        achievements = calculate_achievements(daily_usages, total_stats)
        
        # 7. Tavsiyalar
        recommendations = generate_recommendations(daily_usages, current_streak, total_stats)
        
        data = {
            'user_info': user_info,
            'daily_statistics': daily_statistics,
            'recent_activity': recent_activity,
            'weekly_progress': weekly_progress,
            'monthly_summary': monthly_summary,
            'achievements': achievements,
            'recommendations': recommendations
        }
        
        return Response({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f"{type(e).__name__}: {str(e)}",
            'message': "MyReport ma'lumotlarini olishda xatolik yuz berdi"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_current_streak(daily_usages):
    """Joriy o'qish seriyasini hisoblash"""
    if not daily_usages.exists():
        return 0
    
    streak = 0
    current_date = timezone.now().date()
    
    while True:
        if daily_usages.filter(date=current_date).exists():
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def calculate_longest_streak(daily_usages):
    """Eng uzun o'qish seriyasini hisoblash"""
    if not daily_usages.exists():
        return 0
    
    dates = sorted([usage.date for usage in daily_usages])
    longest_streak = 0
    current_streak = 1
    
    for i in range(1, len(dates)):
        if dates[i] == dates[i-1] + timedelta(days=1):
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1
    
    return max(longest_streak, current_streak)


def get_most_active_day(daily_usages):
    """Eng faol kunni topish"""
    if not daily_usages.exists():
        return None
    
    # Eng ko'p faoliyat qilingan kun
    most_active = daily_usages.annotate(
        total_activity=Count('vocab_learned_count') + 
                   Count('writing_evaluation_count') + 
                   Count('speaking_mock_count') + 
                   Count('reading_attempt_count') + 
                   Count('listening_attempt_count')
    ).order_by('-total_activity').first()
    
    return most_active.date.strftime('%Y-%m-%d') if most_active else None


def get_weekly_progress(daily_usages):
    """Oxirgi 7 kunlik progress"""
    weekly_data = []
    now = timezone.now()
    
    for i in range(7):
        date = (now - timedelta(days=6-i)).date()
        usage = daily_usages.filter(date=date).first()
        
        if usage:
            weekly_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'vocab': usage.vocab_learned_count,
                'writing': usage.writing_evaluation_count,
                'speaking': usage.speaking_mock_count,
                'reading': usage.reading_attempt_count,
                'listening': usage.listening_attempt_count
            })
        else:
            weekly_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'vocab': 0,
                'writing': 0,
                'speaking': 0,
                'reading': 0,
                'listening': 0
            })
    
    return weekly_data


def get_monthly_summary(daily_usages, now):
    """Joriy oylik xulosa"""
    current_month_start = now.replace(day=1).date()
    month_usages = daily_usages.filter(date__gte=current_month_start)
    
    month_stats = month_usages.aggregate(
        total_vocab=Sum('vocab_learned_count'),
        total_writing=Sum('writing_evaluation_count'),
        total_speaking=Sum('speaking_mock_count'),
        total_reading=Sum('reading_attempt_count'),
        total_listening=Sum('listening_attempt_count')
    )
    
    return {
        'current_month_days': month_usages.count(),
        'current_month_vocab': month_stats['total_vocab'] or 0,
        'current_month_writing': month_stats['total_writing'] or 0,
        'current_month_speaking': month_stats['total_speaking'] or 0,
        'current_month_reading': month_stats['total_reading'] or 0,
        'current_month_listening': month_stats['total_listening'] or 0
    }


def calculate_achievements(daily_usages, total_stats):
    """Yutuqlarni hisoblash"""
    return {
        'vocab_master': (total_stats['total_vocab'] or 0) >= 100,
        'writing_champion': (total_stats['total_writing'] or 0) >= 20,
        'speaking_star': (total_stats['total_speaking'] or 0) >= 10,
        'reading_enthusiast': (total_stats['total_reading'] or 0) >= 30,
        'listening_expert': (total_stats['total_listening'] or 0) >= 25,
        'consistency_king': calculate_current_streak(daily_usages) >= 7
    }


def generate_recommendations(daily_usages, current_streak, total_stats):
    """Shaxsiy tavsiyalar generatsiyasi"""
    recommendations = []
    
    # Consistency bo'yicha
    if current_streak < 3:
        recommendations.append("Har kuni kamida bitta faoliyat qiling")
    
    # Vocabulary bo'yicha
    if (total_stats['total_vocab'] or 0) < 50:
        recommendations.append("Vocabulary learningni ko'paytiring")
    
    # Speaking bo'yicha
    if (total_stats['total_speaking'] or 0) < 5:
        recommendations.append("Speaking mock testlariga ko'proq e'tibor bering")
    
    # Writing bo'yicha
    if (total_stats['total_writing'] or 0) < 10:
        recommendations.append("Writing evaluationlarga ko'proq murojaat qiling")
    
    # So'nggi faoliyat
    last_usage = daily_usages.order_by('-date').first()
    if last_usage:
        days_inactive = (timezone.now().date() - last_usage.date).days
        if days_inactive > 2:
            recommendations.append(f"{days_inactive} kundir faoliyat ko'rsatmadingiz, davom eting!")
    
    return recommendations[:5]  # Maksimal 5 ta tavsiya
