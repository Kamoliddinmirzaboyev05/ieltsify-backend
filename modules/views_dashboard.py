from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.permissions import IsAuthenticated
from .models import ListeningTest, ReadingPassage, WritingTask, SmartArticle, ListeningMaterial, VocabularyWord


@swagger_auto_schema(
    method='GET',
    operation_description="Dashboard statistikasi - barcha modulelar uchun to'liq ma'lumot",
    responses={
        200: openapi.Response(
            description="Dashboard statistikasi muvaffaqiyatli olindi",
            examples={
                'application/json': {
                    'success': True,
                    'data': {
                        'overview': {
                            'total_listening_tests': 10,
                            'total_reading_passages': 15,
                            'total_writing_tasks': 8,
                            'total_smart_articles': 12,
                            'total_listening_materials': 20,
                            'total_vocabulary_words': 500,
                        },
                        'active_items': {
                            'active_listening_tests': 8,
                            'active_reading_passages': 12,
                            'active_writing_tasks': 6,
                            'active_listening_materials': 18,
                        }
                    }
                }
            }
        ),
        401: "Unauthorized",
        500: "Internal Server Error"
    },
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_statistics(request):
    """
    Dashboard statistikasi - ekrandagi ma'lumotlar uchun
    """
    try:
        # Umumiy statistika
        total_listening_tests = ListeningTest.objects.count()
        total_reading_passages = ReadingPassage.objects.count()
        total_writing_tasks = WritingTask.objects.count()
        total_smart_articles = SmartArticle.objects.count()
        total_listening_materials = ListeningMaterial.objects.count()
        total_vocabulary_words = VocabularyWord.objects.count()
        
        # Faol (active) itemlar
        active_listening_tests = ListeningTest.objects.filter(is_active=True).count()
        active_reading_passages = ReadingPassage.objects.filter(is_active=True).count()
        active_writing_tasks = WritingTask.objects.filter(is_active=True).count()
        active_listening_materials = ListeningMaterial.objects.filter(is_active=True).count()
        
        # Qiyinlik bo'yicha statistika
        listening_by_difficulty = list(ListeningTest.objects.values('difficulty').annotate(count=Count('id')))
        reading_by_difficulty = list(ReadingPassage.objects.values('difficulty').annotate(count=Count('id')))
        writing_by_difficulty = list(WritingTask.objects.values('difficulty').annotate(count=Count('id')))
        materials_by_difficulty = list(ListeningMaterial.objects.values('difficulty').annotate(count=Count('id')))
        
        # SmartArticle level bo'yicha
        articles_by_level = list(SmartArticle.objects.values('level').annotate(count=Count('id')))
        
        # So'ngi qo'shilganlar (oxirgi 7 kun)
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        recent_listening = ListeningTest.objects.filter(created_at__gte=seven_days_ago).count()
        recent_reading = ReadingPassage.objects.filter(created_at__gte=seven_days_ago).count()
        recent_writing = WritingTask.objects.filter(created_at__gte=seven_days_ago).count()
        recent_articles = SmartArticle.objects.filter(created_at__gte=seven_days_ago).count()
        recent_materials = ListeningMaterial.objects.filter(created_at__gte=seven_days_ago).count()
        recent_vocabulary = VocabularyWord.objects.filter(created_at__gte=seven_days_ago).count()
        
        # User statistikasi
        user = request.user
        user_stats = {}
        
        # Admin bo'lsa barcha statistikani, aks holda o'z statistikasini
        if hasattr(user, 'role') and user.role == 'admin':
            user_stats = {
                'total_vocabulary_words': total_vocabulary_words,
                'public_vocabulary_words': VocabularyWord.objects.filter(is_public=True).count(),
                'private_vocabulary_words': VocabularyWord.objects.filter(is_public=False).count(),
            }
        else:
            user_stats = {
                'total_vocabulary_words': VocabularyWord.objects.filter(created_by=user).count(),
                'imported_vocabulary_words': VocabularyWord.objects.filter(created_by=user, imported_from__isnull=False).count(),
                'created_vocabulary_words': VocabularyWord.objects.filter(created_by=user, imported_from__isnull=True).count(),
            }
        
        data = {
            'success': True,
            'data': {
                'overview': {
                    'total_listening_tests': total_listening_tests,
                    'total_reading_passages': total_reading_passages,
                    'total_writing_tasks': total_writing_tasks,
                    'total_smart_articles': total_smart_articles,
                    'total_listening_materials': total_listening_materials,
                    'total_vocabulary_words': total_vocabulary_words,
                },
                'active_items': {
                    'active_listening_tests': active_listening_tests,
                    'active_reading_passages': active_reading_passages,
                    'active_writing_tasks': active_writing_tasks,
                    'active_listening_materials': active_listening_materials,
                },
                'difficulty_distribution': {
                    'listening_tests': listening_by_difficulty,
                    'reading_passages': reading_by_difficulty,
                    'writing_tasks': writing_by_difficulty,
                    'listening_materials': materials_by_difficulty,
                },
                'articles_by_level': articles_by_level,
                'recent_additions': {
                    'last_7_days': {
                        'listening_tests': recent_listening,
                        'reading_passages': recent_reading,
                        'writing_tasks': recent_writing,
                        'smart_articles': recent_articles,
                        'listening_materials': recent_materials,
                        'vocabulary_words': recent_vocabulary,
                    }
                },
                'user_statistics': user_stats,
                'system_info': {
                    'total_modules': 6,
                    'last_updated': timezone.now().isoformat(),
                }
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        return Response({
            'success': False,
            'error': error_msg,
            'message': 'Dashboard statistikasini olishda xatolik yuz berdi'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='GET',
    operation_description="Tezkor statistika - dashboard uchun qisqacha ma'lumot",
    responses={
        200: openapi.Response(
            description="Tezkor statistika muvaffaqiyatli olindi",
            examples={
                'application/json': {
                    'success': True,
                    'data': {
                        'total_items': {
                            'listening': 10,
                            'reading': 15,
                            'writing': 8,
                            'articles': 12,
                            'materials': 20,
                            'vocabulary': 500,
                        },
                        'active_items': {
                            'listening': 8,
                            'reading': 12,
                            'writing': 6,
                            'materials': 18,
                        }
                    }
                }
            }
        ),
        401: "Unauthorized",
        500: "Internal Server Error"
    },
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quick_stats(request):
    """
    Tezkor statistika - dashboard uchun qisqacha ma'lumot
    """
    try:
        today = date.today()
        data = {
            'success': True,
            'data': {
                'total_items': {
                    'listening': ListeningTest.objects.count(),
                    'reading': ReadingPassage.objects.count(),
                    'writing': WritingTask.objects.count(),
                    'articles': SmartArticle.objects.count(),
                    'materials': ListeningMaterial.objects.count(),
                    'vocabulary': VocabularyWord.objects.count(),
                },
                'active_items': {
                    'listening': ListeningTest.objects.filter(is_active=True).count(),
                    'reading': ReadingPassage.objects.filter(is_active=True).count(),
                    'writing': WritingTask.objects.filter(is_active=True).count(),
                    'materials': ListeningMaterial.objects.filter(is_active=True).count(),
                },
                'recent_count': {
                    'today': {
                        'listening': ListeningTest.objects.filter(created_at__date=today).count(),
                        'reading': ReadingPassage.objects.filter(created_at__date=today).count(),
                        'writing': WritingTask.objects.filter(created_at__date=today).count(),
                        'articles': SmartArticle.objects.filter(created_at__date=today).count(),
                    }
                }
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
