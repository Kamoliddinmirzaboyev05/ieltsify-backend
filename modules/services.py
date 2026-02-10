# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.db import transaction
# from django.db.models import Avg, Count, Sum, Q, F
# from django.core.cache import cache
# import logging
# from .models import (
#     TestCategory, Test, Question, AnswerOption, MatchingItem,
#     TestAttempt, UserAnswer, TestResult, StudyMaterial
# )
# from accounts.services import CoinService
# from subscriptions.services import SubscriptionService
#
# logger = logging.getLogger(__name__)
#
#
# class TestService:
#     """Testlar bilan ishlash uchun service klassi"""
#
#     @staticmethod
#     def get_categories():
#         """Test kategoriyalarini olish"""
#         cache_key = 'test_categories'
#         categories = cache.get(cache_key)
#
#         if not categories:
#             categories = TestCategory.objects.filter(is_active=True).order_by('order')
#             cache.set(cache_key, categories, 60 * 30)  # 30 minutes
#
#         return categories
#
#     @staticmethod
#     def get_tests_by_category(category_id=None, filters=None):
#         """Kategoriya bo'yicha testlarni olish"""
#         queryset = Test.objects.filter(is_active=True)
#
#         if category_id:
#             queryset = queryset.filter(category_id=category_id)
#
#         if filters:
#             if filters.get('difficulty'):
#                 queryset = queryset.filter(difficulty=filters['difficulty'])
#
#             if filters.get('is_premium') is not None:
#                 queryset = queryset.filter(is_premium=filters['is_premium'])
#
#             if filters.get('query'):
#                 queryset = queryset.filter(
#                     Q(title__icontains=filters['query']) |
#                     Q(description__icontains=filters['query'])
#                 )
#
#             if filters.get('min_time'):
#                 queryset = queryset.filter(time_limit_minutes__gte=filters['min_time'])
#
#             if filters.get('max_time'):
#                 queryset = queryset.filter(time_limit_minutes__lte=filters['max_time'])
#
#         return queryset.order_by('-created_at')
#
#     @staticmethod
#     def get_test_detail(test_id):
#         """Test detailini olish"""
#         try:
#             test = Test.objects.get(id=test_id, is_active=True)
#             return test
#         except Test.DoesNotExist:
#             return None
#
#     @staticmethod
#     def start_test(user, test_id):
#         """Testni boshlash"""
#         try:
#             with transaction.atomic():
#                 test = TestService.get_test_detail(test_id)
#                 if not test:
#                     raise ValueError("Test topilmadi")
#
#                 # Subscription limitlarini tekshirish
#                 if test.is_premium:
#                     can_access, message = SubscriptionService.check_subscription_limits(user, 'test')
#                     if not can_access:
#                         raise ValueError(message)
#
#                 # Active attempt borligini tekshirish
#                 active_attempt = TestAttempt.objects.filter(
#                     user=user,
#                     test=test,
#                     status='in_progress'
#                 ).first()
#
#                 if active_attempt:
#                     return active_attempt
#
#                 # Yangi attempt yaratish
#                 attempt = TestAttempt.objects.create(
#                     user=user,
#                     test=test,
#                     status='in_progress',
#                     started_at=timezone.now()
#                 )
#
#                 logger.info(f"Test started: {user.email} -> {test.title}")
#                 return attempt
#
#         except Exception as e:
#             logger.error(f"Error starting test: {str(e)}")
#             raise
#
#     @staticmethod
#     def submit_answer(user, attempt_id, answer_data):
#         """Javobni yuborish"""
#         try:
#             with transaction.atomic():
#                 attempt = TestAttempt.objects.get(
#                     id=attempt_id,
#                     user=user,
#                     status='in_progress'
#                 )
#
#                 question_id = answer_data['question_id']
#                 question = Question.objects.get(id=question_id)
#
#                 # Mavjud javobni tekshirish
#                 existing_answer = UserAnswer.objects.filter(
#                     attempt=attempt,
#                     question=question
#                 ).first()
#
#                 if existing_answer:
#                     user_answer = existing_answer
#                 else:
#                     user_answer = UserAnswer.objects.create(
#                         attempt=attempt,
#                         question=question
#                     )
#
#                 # Javobni saqlash
#                 if question.question_type in ['multiple_choice', 'true_false']:
#                     user_answer.selected_answer = answer_data.get('selected_answer')
#                 elif question.question_type in ['short_answer', 'essay']:
#                     user_answer.written_answer = answer_data.get('written_answer')
#                 elif question.question_type == 'matching':
#                     user_answer.matching_answers = answer_data.get('matching_answers')
#
#                 user_answer.time_spent_seconds = answer_data.get('time_spent_seconds', 0)
#                 user_answer.answered_at = timezone.now()
#
#                 # Javobni tekshirish va ballarni hisoblash
#                 TestService._evaluate_answer(user_answer, question)
#                 user_answer.save()
#
#                 logger.info(f"Answer submitted: {user.email} -> Question {question_id}")
#                 return user_answer
#
#         except TestAttempt.DoesNotExist:
#             raise ValueError("Test attempt topilmadi yoki tugagan")
#         except Question.DoesNotExist:
#             raise ValueError("Savol topilmadi")
#         except Exception as e:
#             logger.error(f"Error submitting answer: {str(e)}")
#             raise
#
#     @staticmethod
#     def _evaluate_answer(user_answer, question):
#         """Javobni baholash"""
#         is_correct = False
#         points_earned = 0
#
#         if question.question_type == 'multiple_choice':
#             is_correct = user_answer.selected_answer == question.correct_answer
#             points_earned = question.points if is_correct else 0
#
#         elif question.question_type == 'true_false':
#             is_correct = user_answer.selected_answer == question.correct_answer
#             points_earned = question.points if is_correct else 0
#
#         elif question.question_type == 'short_answer':
#             # Simple text matching (case-insensitive)
#             if question.correct_answer:
#                 is_correct = user_answer.written_answer.lower().strip() == question.correct_answer.lower().strip()
#                 points_earned = question.points if is_correct else 0
#
#         elif question.question_type == 'essay':
#             # Essay uchun avtomatik tekshirish murakkab, hozircha 0
#             points_earned = 0
#
#         elif question.question_type == 'matching':
#             # Matching answers tekshirish
#             if question.correct_answer and user_answer.matching_answers:
#                 is_correct = user_answer.matching_answers == question.correct_answer
#                 points_earned = question.points if is_correct else 0
#
#         user_answer.is_correct = is_correct
#         user_answer.points_earned = points_earned
#
#     @staticmethod
#     def complete_test(user, attempt_id):
#         """Testni tugatish"""
#         try:
#             with transaction.atomic():
#                 attempt = TestAttempt.objects.get(
#                     id=attempt_id,
#                     user=user,
#                     status='in_progress'
#                 )
#
#                 test = attempt.test
#
#                 # Testni tugatish
#                 attempt.status = 'completed'
#                 attempt.completed_at = timezone.now()
#                 attempt.time_spent_seconds = int(
#                     (attempt.completed_at - attempt.started_at).total_seconds()
#                 )
#                 attempt.save()
#
#                 # Natijalarni hisoblash
#                 result = TestService._calculate_test_result(attempt, test)
#
#                 # Usage ni oshirish
#                 SubscriptionService.increment_usage(user, 'test')
#
#                 logger.info(f"Test completed: {user.email} -> {test.title}")
#                 return attempt, result
#
#         except TestAttempt.DoesNotExist:
#             raise ValueError("Test attempt topilmadi yoki tugagan")
#         except Exception as e:
#             logger.error(f"Error completing test: {str(e)}")
#             raise
#
#     @staticmethod
#     def _calculate_test_result(attempt, test):
#         """Test natijalarini hisoblash"""
#         answers = attempt.answers.all()
#
#         total_score = sum(answer.points_earned for answer in answers)
#         max_score = sum(answer.question.points for answer in answers)
#         percentage = (total_score / max_score * 100) if max_score > 0 else 0
#
#         # IELTS band score hisoblash
#         band_score = TestService._calculate_band_score(percentage)
#
#         # Performance level
#         if percentage >= 90:
#             performance_level = 'Excellent'
#         elif percentage >= 80:
#             performance_level = 'Good'
#         elif percentage >= 70:
#             performance_level = 'Satisfactory'
#         elif percentage >= 60:
#             performance_level = 'Needs Improvement'
#         else:
#             performance_level = 'Poor'
#
#         # Feedback va recommendations
#         feedback = TestService._generate_feedback(percentage, test.category.name)
#         recommendations = TestService._generate_recommendations(attempt, test)
#
#         # Result yaratish
#         result = TestResult.objects.create(
#             attempt=attempt,
#             total_score=total_score,
#             max_score=max_score,
#             percentage=percentage,
#             band_score=band_score,
#             performance_level=performance_level,
#             feedback=feedback,
#             recommendations=recommendations
#         )
#
#         return result
#
#     @staticmethod
#     def _calculate_band_score(percentage):
#         """IELTS band score hisoblash"""
#         if percentage >= 95:
#             return 9.0
#         elif percentage >= 90:
#             return 8.5
#         elif percentage >= 85:
#             return 8.0
#         elif percentage >= 80:
#             return 7.5
#         elif percentage >= 75:
#             return 7.0
#         elif percentage >= 70:
#             return 6.5
#         elif percentage >= 65:
#             return 6.0
#         elif percentage >= 60:
#             return 5.5
#         elif percentage >= 55:
#             return 5.0
#         elif percentage >= 50:
#             return 4.5
#         elif percentage >= 45:
#             return 4.0
#         elif percentage >= 40:
#             return 3.5
#         else:
#             return 3.0
#
#     @staticmethod
#     def _generate_feedback(percentage, category_name):
#         """Feedback generatsiya qilish"""
#         if percentage >= 90:
#             return f"Excellent work! Your {category_name} skills are outstanding."
#         elif percentage >= 80:
#             return f"Good job! Your {category_name} skills are strong."
#         elif percentage >= 70:
#             return f"Satisfactory performance. Keep practicing {category_name}."
#         elif percentage >= 60:
#             return f"Your {category_name} skills need improvement."
#         else:
#             return f"Significant practice needed in {category_name}."
#
#     @staticmethod
#     def _generate_recommendations(attempt, test):
#         """Recommendations generatsiya qilish"""
#         recommendations = []
#
#         # Question type bo'yicha tahlil
#         answers_by_type = {}
#         for answer in attempt.answers.all():
#             qtype = answer.question.question_type
#             if qtype not in answers_by_type:
#                 answers_by_type[qtype] = {'correct': 0, 'total': 0}
#
#             answers_by_type[qtype]['total'] += 1
#             if answer.is_correct:
#                 answers_by_type[qtype]['correct'] += 1
#
#         # Weak areas ni aniqlash
#         for qtype, stats in answers_by_type.items():
#             accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
#             if accuracy < 60:
#                 recommendations.append(f"Practice more {qtype} questions")
#
#         if not recommendations:
#             recommendations.append("Keep up the good work!")
#
#         return recommendations
#
#     @staticmethod
#     def get_user_attempts(user, test_id=None, status=None):
#         """Foydalanuvchi test urinishlarini olish"""
#         queryset = TestAttempt.objects.filter(user=user)
#
#         if test_id:
#             queryset = queryset.filter(test_id=test_id)
#
#         if status:
#             queryset = queryset.filter(status=status)
#
#         return queryset.order_by('-created_at')
#
#     @staticmethod
#     def get_test_stats(user):
#         """Foydalanuvchi test statistikasini olish"""
#         attempts = TestAttempt.objects.filter(user=user, status='completed')
#
#         if not attempts.exists():
#             return {
#                 'total_tests': 0,
#                 'completed_tests': 0,
#                 'average_score': 0,
#                 'best_score': 0,
#                 'total_time_spent': 0,
#                 'average_band_score': 0
#             }
#
#         total_tests = attempts.count()
#         total_score = 0
#         max_score = 0
#         total_time = 0
#         total_band = 0
#
#         for attempt in attempts:
#             if attempt.result:
#                 total_score += attempt.result.percentage
#                 total_band += attempt.result.band_score
#                 max_score = max(max_score, attempt.result.percentage)
#
#             total_time += attempt.time_spent_seconds
#
#         return {
#             'total_tests': total_tests,
#             'completed_tests': total_tests,
#             'average_score': total_score / total_tests,
#             'best_score': max_score,
#             'total_time_spent': total_time,
#             'average_band_score': total_band / total_tests
#         }
#
#     @staticmethod
#     def get_leaderboard(category_id=None, limit=10):
#         """Leaderboardni olish"""
#         cache_key = f'leaderboard_{category_id}_{limit}'
#         leaderboard = cache.get(cache_key)
#
#         if not leaderboard:
#             queryset = TestAttempt.objects.filter(
#                 status='completed',
#                 result__isnull=False
#             )
#
#             if category_id:
#                 queryset = queryset.filter(test__category_id=category_id)
#
#             leaderboard = queryset.values('user__email').annotate(
#                 total_score=Avg('result__percentage'),
#                 tests_completed=Count('id'),
#                 average_band=Avg('result__band_score')
#             ).order_by('-total_score')[:limit]
#
#             # Rank qo'shish
#             for i, entry in enumerate(leaderboard, 1):
#                 entry['rank'] = i
#
#             cache.set(cache_key, leaderboard, 60 * 15)  # 15 minutes
#
#         return leaderboard
#
#     @staticmethod
#     def get_recommendations(user, limit=5):
#         """Personalized tavsiyalar"""
#         # Foydalanuvchining weak areas ni aniqlash
#         attempts = TestAttempt.objects.filter(
#             user=user,
#             status='completed',
#             result__isnull=False
#         )
#
#         if not attempts.exists():
#             # Yangi foydalanuvchi uchun oddiy testlar
#             return Test.objects.filter(
#                 difficulty='beginner',
#                 is_active=True
#             ).order_by('?')[:limit]
#
#         # Performance bo'yicha tavsiyalar
#         category_performance = {}
#         for attempt in attempts:
#             category = attempt.test.category
#             if category not in category_performance:
#                 category_performance[category] = []
#             category_performance[category].append(attempt.result.percentage)
#
#         # Eng past performance bo'yicha category
#         weak_category = None
#         worst_performance = 100
#
#         for category, scores in category_performance.items():
#             avg_score = sum(scores) / len(scores)
#             if avg_score < worst_performance:
#                 worst_performance = avg_score
#                 weak_category = category
#
#         if weak_category:
#             # Weak category bo'yicha testlar
#             return Test.objects.filter(
#                 category=weak_category,
#                 difficulty='beginner',
#                 is_active=True
#             ).order_by('?')[:limit]
#
#         # Random testlar
#         return Test.objects.filter(
#             is_active=True
#         ).order_by('?')[:limit]
#
#
# class StudyMaterialService:
#     """Study materiallar bilan ishlash uchun service"""
#
#     @staticmethod
#     def get_materials(category_id=None, filters=None):
#         """Study materiallarni olish"""
#         queryset = StudyMaterial.objects.all()
#
#         if category_id:
#             queryset = queryset.filter(category_id=category_id)
#
#         if filters:
#             if filters.get('material_type'):
#                 queryset = queryset.filter(material_type=filters['material_type'])
#
#             if filters.get('difficulty'):
#                 queryset = queryset.filter(difficulty=filters['difficulty'])
#
#             if filters.get('is_premium') is not None:
#                 queryset = queryset.filter(is_premium=filters['is_premium'])
#
#             if filters.get('query'):
#                 queryset = queryset.filter(
#                     Q(title__icontains=filters['query']) |
#                     Q(description__icontains=filters['query'])
#                 )
#
#         return queryset.order_by('order', '-created_at')
#
#     @staticmethod
#     def get_material_detail(material_id):
#         """Study material detailini olish"""
#         try:
#             material = StudyMaterial.objects.get(id=material_id)
#
#             # View count ni oshirish
#             material.view_count += 1
#             material.save(update_fields=['view_count'])
#
#             return material
#         except StudyMaterial.DoesNotExist:
#             return None
#
#     @staticmethod
#     def access_material(user, material_id):
#         """Study materialga kirish"""
#         try:
#             material = StudyMaterialService.get_material_detail(material_id)
#             if not material:
#                 raise ValueError("Material topilmadi")
#
#             # Premium material uchun tekshirish
#             if material.is_premium:
#                 can_access, message = SubscriptionService.check_subscription_limits(user, 'study_material')
#                 if not can_access:
#                     raise ValueError(message)
#
#                 # Usage ni oshirish
#                 SubscriptionService.increment_usage(user, 'study_material')
#
#             logger.info(f"Material accessed: {user.email} -> {material.title}")
#             return material
#
#         except Exception as e:
#             logger.error(f"Error accessing material: {str(e)}")
#             raise
#
#
# class TestAnalyticsService:
#     """Test analytics uchun service"""
#
#     @staticmethod
#     def get_user_analytics(user, days=30):
#         """Foydalanuvchi analyticsini olish"""
#         from_date = timezone.now() - timedelta(days=days)
#
#         attempts = TestAttempt.objects.filter(
#             user=user,
#             created_at__gte=from_date
#         ).select_related('test', 'test__category', 'result')
#
#         if not attempts.exists():
#             return {
#                 'total_attempts': 0,
#                 'average_score': 0,
#                 'improvement_rate': 0,
#                 'strong_areas': [],
#                 'weak_areas': [],
#                 'time_management': {},
#                 'accuracy_by_question_type': {},
#                 'progress_over_time': []
#             }
#
#         # Umumiy statistika
#         completed_attempts = attempts.filter(status='completed')
#         total_attempts = completed_attempts.count()
#
#         if total_attempts == 0:
#             average_score = 0
#         else:
#             average_score = sum(a.result.percentage for a in completed_attempts if a.result) / total_attempts
#
#         # Improvement rate
#         if total_attempts >= 2:
#             first_half = completed_attempts[:total_attempts//2]
#             second_half = completed_attempts[total_attempts//2:]
#
#             first_avg = sum(a.result.percentage for a in first_half if a.result) / len(first_half) if first_half else 0
#             second_avg = sum(a.result.percentage for a in second_half if a.result) / len(second_half) if second_half else 0
#
#             improvement_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
#         else:
#             improvement_rate = 0
#
#         # Category bo'yicha performance
#         category_stats = {}
#         for attempt in completed_attempts:
#             if attempt.result:
#                 category = attempt.test.category.name
#                 if category not in category_stats:
#                     category_stats[category] = []
#                 category_stats[category].append(attempt.result.percentage)
#
#         strong_areas = []
#         weak_areas = []
#
#         for category, scores in category_stats.items():
#             avg_score = sum(scores) / len(scores)
#             if avg_score >= 80:
#                 strong_areas.append(category)
#             elif avg_score < 60:
#                 weak_areas.append(category)
#
#         # Time management
#         total_time = sum(attempt.time_spent_seconds for attempt in completed_attempts)
#         avg_time = total_time / total_attempts if total_attempts > 0 else 0
#
#         # Question type accuracy
#         question_type_stats = {}
#         for attempt in completed_attempts:
#             for answer in attempt.answers.all():
#                 qtype = answer.question.question_type
#                 if qtype not in question_type_stats:
#                     question_type_stats[qtype] = {'correct': 0, 'total': 0}
#
#                 question_type_stats[qtype]['total'] += 1
#                 if answer.is_correct:
#                     question_type_stats[qtype]['correct'] += 1
#
#         accuracy_by_type = {}
#         for qtype, stats in question_type_stats.items():
#             accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
#             accuracy_by_type[qtype] = accuracy
#
#         # Progress over time
#         progress_data = []
#         for attempt in completed_attempts:
#             if attempt.result:
#                 progress_data.append({
#                     'date': attempt.created_at.date().isoformat(),
#                     'score': attempt.result.percentage,
#                     'band_score': attempt.result.band_score
#                 })
#
#         return {
#             'total_attempts': total_attempts,
#             'average_score': average_score,
#             'improvement_rate': improvement_rate,
#             'strong_areas': strong_areas,
#             'weak_areas': weak_areas,
#             'time_management': {
#                 'total_time_seconds': total_time,
#                 'average_time_seconds': avg_time
#             },
#             'accuracy_by_question_type': accuracy_by_type,
#             'progress_over_time': progress_data
#         }
