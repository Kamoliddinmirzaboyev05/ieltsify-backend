# from datetime import datetime, timedelta
# from django.utils import timezone
# from django.db import transaction
# from django.db.models import Avg, Count, Sum, Q, F
# from django.core.cache import cache
# import logging
# from .models import (
#     TestSession, SectionAttempt, QuestionResponse, ProgressTracker,
#     StudySession, ErrorLog, Recommendation
# )
# from modules.models import Test, Question
# from modules.services import TestService
# from subscriptions.services import SubscriptionService
#
# logger = logging.getLogger(__name__)
#
#
# class TestSessionService:
#     """Test sessiyalari bilan ishlash uchun service klassi"""
#
#     @staticmethod
#     def start_session(user, session_data):
#         """Test sessiyasini boshlash"""
#         try:
#             with transaction.atomic():
#                 session = TestSession.objects.create(
#                     user=user,
#                     title=session_data['title'],
#                     description=session_data.get('description', ''),
#                     session_type=session_data.get('session_type', 'full_test'),
#                     status='active'
#                 )
#
#                 # Agar custom session bo'lsa, testlarni qo'shish
#                 if session.session_type == 'custom' and session_data.get('test_ids'):
#                     # Bu yerda custom testlarni qo'shish logikasi
#                     pass
#
#                 logger.info(f"Test session started: {user.email} -> {session.title}")
#                 return session
#
#         except Exception as e:
#             logger.error(f"Error starting test session: {str(e)}")
#             raise
#
#     @staticmethod
#     def start_section(user, session_id, section_data):
#         """Test bo'limini boshlash"""
#         try:
#             with transaction.atomic():
#                 session = TestSession.objects.get(
#                     id=session_id,
#                     user=user,
#                     status='active'
#                 )
#
#                 test_id = section_data['test_id']
#                 section_type = section_data['section_type']
#
#                 test = Test.objects.get(id=test_id, is_active=True)
#
#                 # Subscription limitlarini tekshirish
#                 if test.is_premium:
#                     can_access, message = SubscriptionService.check_subscription_limits(user, 'test')
#                     if not can_access:
#                         raise ValueError(message)
#
#                 # Section attempt yaratish
#                 section_attempt = SectionAttempt.objects.create(
#                     session=session,
#                     user=user,
#                     test=test,
#                     section_type=section_type,
#                     status='in_progress',
#                     started_at=timezone.now()
#                 )
#
#                 logger.info(f"Section started: {user.email} -> {test.title} ({section_type})")
#                 return section_attempt
#
#         except TestSession.DoesNotExist:
#             raise ValueError("Test sessiyasi topilmadi yoki nofaol")
#         except Test.DoesNotExist:
#             raise ValueError("Test topilmadi yoki nofaol")
#         except Exception as e:
#             logger.error(f"Error starting section: {str(e)}")
#             raise
#
#     @staticmethod
#     def submit_response(user, section_id, response_data):
#         """Javobni yuborish"""
#         try:
#             with transaction.atomic():
#                 section = SectionAttempt.objects.get(
#                     id=section_id,
#                     user=user,
#                     status='in_progress'
#                 )
#
#                 question_id = response_data['question_id']
#                 question = Question.objects.get(id=question_id)
#
#                 # Mavjud javobni tekshirish
#                 existing_response = QuestionResponse.objects.filter(
#                     section_attempt=section,
#                     question=question
#                 ).first()
#
#                 if existing_response:
#                     response = existing_response
#                 else:
#                     response = QuestionResponse.objects.create(
#                         section_attempt=section,
#                         question=question
#                     )
#
#                 # Javobni saqlash
#                 response.selected_answer = response_data.get('selected_answer')
#                 response.written_answer = response_data.get('written_answer')
#                 response.matching_answers = response_data.get('response')
#                 response.time_spent_seconds = response_data.get('time_spent_seconds', 0)
#                 response.answered_at = timezone.now()
#                 response.status = 'answered'
#
#                 # Javobni tekshirish
#                 TestSessionService._evaluate_response(response, question)
#                 response.save()
#
#                 logger.info(f"Response submitted: {user.email} -> Question {question_id}")
#                 return response
#
#         except SectionAttempt.DoesNotExist:
#             raise ValueError("Bo'lim topilmadi yoki tugagan")
#         except Question.DoesNotExist:
#             raise ValueError("Savol topilmadi")
#         except Exception as e:
#             logger.error(f"Error submitting response: {str(e)}")
#             raise
#
#     @staticmethod
#     def _evaluate_response(response, question):
#         """Javobni baholash"""
#         is_correct = False
#         points_earned = 0
#
#         if question.question_type in ['multiple_choice', 'true_false']:
#             if response.selected_answer:
#                 is_correct = response.selected_answer == question.correct_answer
#                 points_earned = question.points if is_correct else 0
#
#         elif question.question_type in ['short_answer', 'essay']:
#             if response.written_answer:
#                 # Simple text matching for short answer
#                 if question.correct_answer:
#                     is_correct = response.written_answer.lower().strip() == question.correct_answer.lower().strip()
#                     points_earned = question.points if is_correct else 0
#
#         elif question.question_type == 'matching':
#             if response.matching_answers and question.correct_answer:
#                 is_correct = response.matching_answers == question.correct_answer
#                 points_earned = question.points if is_correct else 0
#
#         response.is_correct = is_correct
#         response.points_earned = points_earned
#
#     @staticmethod
#     def complete_section(user, section_id):
#         """Bo'limni tugatish"""
#         try:
#             with transaction.atomic():
#                 section = SectionAttempt.objects.get(
#                     id=section_id,
#                     user=user,
#                     status='in_progress'
#                 )
#
#                 # Bo'limni tugatish
#                 section.status = 'completed'
#                 section.completed_at = timezone.now()
#
#                 # Statistikani hisoblash
#                 responses = section.question_responses.all()
#                 section.total_questions = responses.count()
#                 section.correct_answers = responses.filter(is_correct=True).count()
#                 section.skipped_questions = responses.filter(status='skipped').count()
#
#                 # Ballarni hisoblash
#                 total_points = sum(question.points for question in section.test.questions.all())
#                 earned_points = sum(response.points_earned for response in responses)
#
#                 section.score = earned_points
#                 section.percentage = (earned_points / total_points * 100) if total_points > 0 else 0
#
#                 # IELTS band score
#                 section.band_score = TestService._calculate_band_score(section.percentage)
#
#                 section.save()
#
#                 # Progress tracker ni yangilash
#                 TestSessionService._update_progress_tracker(user, section.test.category, section.percentage)
#
#                 # Usage ni oshirish
#                 SubscriptionService.increment_usage(user, 'test')
#
#                 logger.info(f"Section completed: {user.email} -> {section.test.title}")
#                 return section
#
#         except SectionAttempt.DoesNotExist:
#             raise ValueError("Bo'lim topilmadi yoki tugagan")
#         except Exception as e:
#             logger.error(f"Error completing section: {str(e)}")
#             raise
#
#     @staticmethod
#     def complete_session(user, session_id):
#         """Test sessiyasini tugatish"""
#         try:
#             with transaction.atomic():
#                 session = TestSession.objects.get(
#                     id=session_id,
#                     user=user,
#                     status='active'
#                 )
#
#                 # Sessiyani tugatish
#                 session.status = 'completed'
#                 session.completed_at = timezone.now()
#
#                 # Umumiy statistikani hisoblash
#                 sections = session.section_attempts.all()
#                 if sections.exists():
#                     total_score = sum(section.score for section in sections if section.score)
#                     total_percentage = sum(section.percentage for section in sections if section.percentage) / sections.count()
#
#                     session.total_score = total_score
#                     session.total_percentage = total_percentage
#                     session.overall_band = TestService._calculate_band_score(total_percentage)
#
#                 session.save()
#
#                 logger.info(f"Test session completed: {user.email} -> {session.title}")
#                 return session
#
#         except TestSession.DoesNotExist:
#             raise ValueError("Test sessiyasi topilmadi yoki nofaol")
#         except Exception as e:
#             logger.error(f"Error completing session: {str(e)}")
#             raise
#
#     @staticmethod
#     def _update_progress_tracker(user, category, percentage):
#         """Progress trackerni yangilash"""
#         tracker, created = ProgressTracker.objects.get_or_create(
#             user=user,
#             category=category,
#             defaults={
#                 'total_tests_taken': 1,
#                 'average_score': percentage,
#                 'best_score': percentage,
#                 'current_band': TestService._calculate_band_score(percentage),
#                 'last_activity_date': timezone.now().date()
#             }
#         )
#
#         if not created:
#             # Statistikani yangilash
#             total_tests = tracker.total_tests_taken + 1
#             avg_score = (tracker.average_score * tracker.total_tests_taken + percentage) / total_tests
#             best_score = max(tracker.best_score, percentage)
#             current_band = TestService._calculate_band_score(avg_score)
#
#             tracker.total_tests_taken = total_tests
#             tracker.average_score = avg_score
#             tracker.best_score = best_score
#             tracker.current_band = current_band
#             tracker.last_activity_date = timezone.now().date()
#             tracker.update_progress()
#             tracker.save()
#
#     @staticmethod
#     def get_user_sessions(user, status=None, limit=20):
#         """Foydalanuvchi sessiyalarini olish"""
#         queryset = TestSession.objects.filter(user=user)
#
#         if status:
#             queryset = queryset.filter(status=status)
#
#         return queryset.order_by('-created_at')[:limit]
#
#     @staticmethod
#     def get_session_analytics(user, days=30):
#         """Sessiya analyticsini olish"""
#         from_date = timezone.now() - timedelta(days=days)
#
#         sessions = TestSession.objects.filter(
#             user=user,
#             created_at__gte=from_date
#         ).select_related('section_attempts__test')
#
#         if not sessions.exists():
#             return {
#                 'total_sessions': 0,
#                 'completed_sessions': 0,
#                 'average_score': 0,
#                 'average_band': 0,
#                 'total_time_spent': 0,
#                 'improvement_rate': 0,
#                 'section_performance': {},
#                 'recent_sessions': []
#             }
#
#         completed_sessions = sessions.filter(status='completed')
#         total_sessions = completed_sessions.count()
#
#         if total_sessions == 0:
#             return {
#                 'total_sessions': 0,
#                 'completed_sessions': 0,
#                 'average_score': 0,
#                 'average_band': 0,
#                 'total_time_spent': 0,
#                 'improvement_rate': 0,
#                 'section_performance': {},
#                 'recent_sessions': []
#             }
#
#         # Umumiy statistika
#         average_score = sum(s.total_score for s in completed_sessions if s.total_score) / total_sessions
#         average_band = sum(s.overall_band for s in completed_sessions if s.overall_band) / total_sessions
#         total_time = sum(s.get_duration_minutes() for s in completed_sessions)
#
#         # Improvement rate
#         if total_sessions >= 2:
#             first_half = completed_sessions[:total_sessions//2]
#             second_half = completed_sessions[total_sessions//2:]
#
#             first_avg = sum(s.total_score for s in first_half if s.total_score) / len(first_half) if first_half else 0
#             second_avg = sum(s.total_score for s in second_half if s.total_score) / len(second_half) if second_half else 0
#
#             improvement_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
#         else:
#             improvement_rate = 0
#
#         # Section performance
#         section_performance = {}
#         for session in completed_sessions:
#             for section in session.section_attempts.all():
#                 section_type = section.get_section_type_display()
#                 if section_type not in section_performance:
#                     section_performance[section_type] = []
#                 if section.percentage:
#                     section_performance[section_type].append(section.percentage)
#
#         # Calculate averages for each section type
#         for section_type in section_performance:
#             scores = section_performance[section_type]
#             section_performance[section_type] = sum(scores) / len(scores) if scores else 0
#
#         return {
#             'total_sessions': total_sessions,
#             'completed_sessions': total_sessions,
#             'average_score': average_score,
#             'average_band': average_band,
#             'total_time_spent': total_time,
#             'improvement_rate': improvement_rate,
#             'section_performance': section_performance,
#             'recent_sessions': TestSessionSerializer(
#                 sessions.order_by('-created_at')[:5],
#                 many=True
#             ).data
#         }
#
#
# class StudySessionService:
#     """Study sessiyalari bilan ishlash uchun service"""
#
#     @staticmethod
#     def start_study_session(user, session_data):
#         """Study sessiyasini boshlash"""
#         try:
#             with transaction.atomic():
#                 material_id = session_data['material_id']
#                 session_type = session_data.get('session_type', 'study')
#
#                 from modules.models import StudyMaterial
#                 material = StudyMaterial.objects.get(id=material_id)
#
#                 # Premium material uchun tekshirish
#                 if material.is_premium:
#                     can_access, message = SubscriptionService.check_subscription_limits(user, 'study_material')
#                     if not can_access:
#                         raise ValueError(message)
#
#                 session = StudySession.objects.create(
#                     user=user,
#                     material=material,
#                     session_type=session_type,
#                     started_at=timezone.now()
#                 )
#
#                 logger.info(f"Study session started: {user.email} -> {material.title}")
#                 return session
#
#         except StudyMaterial.DoesNotExist:
#             raise ValueError("Material topilmadi")
#         except Exception as e:
#             logger.error(f"Error starting study session: {str(e)}")
#             raise
#
#     @staticmethod
#     def update_study_session(user, session_id, update_data):
#         """Study sessiyasini yangilash"""
#         try:
#             with transaction.atomic():
#                 session = StudySession.objects.get(
#                     id=session_id,
#                     user=user,
#                     completed_at__isnull=True
#                 )
#
#                 if 'completion_percentage' in update_data:
#                     session.completion_percentage = update_data['completion_percentage']
#
#                 if 'rating' in update_data:
#                     session.rating = update_data['rating']
#
#                 if 'notes' in update_data:
#                     session.notes = update_data['notes']
#
#                 # Agar 100% bo'lsa, sessiyani tugatish
#                 if session.completion_percentage >= 100:
#                     session.completed_at = timezone.now()
#                     session.duration_minutes = int(
#                         (session.completed_at - session.started_at).total_seconds() / 60
#                     )
#
#                 session.save()
#
#                 logger.info(f"Study session updated: {user.email} -> Session {session_id}")
#                 return session
#
#         except StudySession.DoesNotExist:
#             raise ValueError("Study sessiyasi topilmadi yoki tugagan")
#         except Exception as e:
#             logger.error(f"Error updating study session: {str(e)}")
#             raise
#
#     @staticmethod
#     def get_user_study_sessions(user, limit=20):
#         """Foydalanuvchi study sessiyalarini olish"""
#         return StudySession.objects.filter(
#             user=user
#         ).order_by('-created_at')[:limit]
#
#     @staticmethod
#     def get_study_analytics(user, days=30):
#         """Study analyticsini olish"""
#         from_date = timezone.now() - timedelta(days=days)
#
#         sessions = StudySession.objects.filter(
#             user=user,
#             created_at__gte=from_date
#         ).select_related('material')
#
#         if not sessions.exists():
#             return {
#                 'total_sessions': 0,
#                 'total_time_spent': 0,
#                 'average_session_duration': 0,
#                 'preferred_materials': [],
#                 'study_patterns': {},
#                 'productivity_trends': []
#             }
#
#         total_sessions = sessions.count()
#         completed_sessions = sessions.filter(completed_at__isnull=False)
#         total_time = sum(session.duration_minutes for session in completed_sessions if session.duration_minutes)
#         avg_duration = total_time / completed_sessions.count() if completed_sessions.count() > 0 else 0
#
#         # Preferred materials
#         material_counts = sessions.values('material__title').annotate(count=Count('id')).order_by('-count')[:5]
#
#         # Study patterns (by hour of day)
#         study_patterns = {}
#         for session in sessions:
#             hour = session.started_at.hour
#             study_patterns[hour] = study_patterns.get(hour, 0) + 1
#
#         return {
#             'total_sessions': total_sessions,
#             'total_time_spent': total_time,
#             'average_session_duration': avg_duration,
#             'preferred_materials': list(material_counts),
#             'study_patterns': study_patterns,
#             'productivity_trends': []  # Could be implemented with time series data
#         }
#
#
# class ErrorAnalysisService:
#     """Xatolik tahlili uchun service"""
#
#     @staticmethod
#     def log_error(user, question_id, error_data):
#         """Xatolikni yozish"""
#         try:
#             question = Question.objects.get(id=question_id)
#
#             error_log, created = ErrorLog.objects.get_or_create(
#                 user=user,
#                 question=question,
#                 defaults={
#                     'error_type': error_data.get('error_type', 'incorrect_answer'),
#                     'user_answer': error_data.get('user_answer'),
#                     'correct_answer': question.correct_answer,
#                     'explanation': error_data.get('explanation'),
#                     'occurrence_count': 1,
#                     'first_occurrence': timezone.now(),
#                     'last_occurrence': timezone.now()
#                 }
#             )
#
#             if not created:
#                 # Mavjud xatolikni yangilash
#                 error_log.occurrence_count += 1
#                 error_log.last_occurrence = timezone.now()
#                 error_log.save()
#
#             logger.info(f"Error logged: {user.email} -> Question {question_id}")
#             return error_log
#
#         except Question.DoesNotExist:
#             raise ValueError("Savol topilmadi")
#         except Exception as e:
#             logger.error(f"Error logging error: {str(e)}")
#             raise
#
#     @staticmethod
#     def get_error_analysis(user, days=30):
#         """Xatolik tahlilini olish"""
#         from_date = timezone.now() - timedelta(days=days)
#
#         errors = ErrorLog.objects.filter(
#             user=user,
#             created_at__gte=from_date
#         ).select_related('question', 'question__test', 'question__test__category')
#
#         if not errors.exists():
#             return {
#                 'total_errors': 0,
#                 'error_by_type': {},
#                 'error_by_category': {},
#                 'most_common_errors': [],
#                 'improvement_trends': {}
#             }
#
#         # Error by type
#         error_by_type = {}
#         for error in errors:
#             error_type = error.get_error_type_display()
#             error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
#
#         # Error by category
#         error_by_category = {}
#         for error in errors:
#             category = error.question.test.category.name
#             error_by_category[category] = error_by_category.get(category, 0) + 1
#
#         # Most common errors
#         most_common = errors.order_by('-occurrence_count')[:10]
#
#         return {
#             'total_errors': errors.count(),
#             'error_by_type': error_by_type,
#             'error_by_category': error_by_category,
#             'most_common_errors': [
#                 {
#                     'question_text': error.question.question_text[:100] + "...",
#                     'error_type': error.get_error_type_display(),
#                     'occurrence_count': error.occurrence_count,
#                     'last_occurrence': error.last_occurrence
#                 }
#                 for error in most_common
#             ],
#             'improvement_trends': {}  # Could be implemented with time series analysis
#         }
#
#
# class RecommendationService:
#     """Tavsiyalar uchun service"""
#
#     @staticmethod
#     def generate_recommendations(user):
#         """Personalized tavsiyalarni generatsiya qilish"""
#         try:
#             recommendations = []
#
#             # Progress tracker asosida tavsiyalar
#             progress_trackers = ProgressTracker.objects.filter(user=user)
#
#             for tracker in progress_trackers:
#                 if tracker.average_score < 60:
#                     recommendations.append(
#                         Recommendation.objects.create(
#                             user=user,
#                             title=f"{tracker.category.name} bo'yicha ko'proq mashq qiling",
#                             description=f"Sizning {tracker.category.name} ko'rsatkichingiz {tracker.average_score:.1f}%. Ko'proq mashq qilish tavsiya etiladi.",
#                             recommendation_type='practice',
#                             target_skill=tracker.category.name,
#                             priority='high'
#                         )
#                     )
#                 elif tracker.average_score < 80:
#                     recommendations.append(
#                         Recommendation.objects.create(
#                             user=user,
#                             title=f"{tracker.category.name} bo'yicha takomillashtirish",
#                             description=f"{tracker.category.name} bo'yicha ko'nikmalaringizni yaxshilash uchun qo'shimcha materiallarni o'rganing.",
#                             recommendation_type='improvement',
#                             target_skill=tracker.category.name,
#                             priority='medium'
#                         )
#                     )
#
#             # Error analysis asosida tavsiyalar
#             error_analysis = ErrorAnalysisService.get_error_analysis(user)
#             if error_analysis['total_errors'] > 5:
#                 recommendations.append(
#                     Recommendation.objects.create(
#                         user=user,
#                         title="Xatoliklarni tahlil qiling",
#                         description="So'nggi 30 kun ichida ko'p xatoliklar qayd etilgan. Xatoliklarni tahlil qilish va ular ustida ishlash tavsiya etiladi.",
#                         recommendation_type='error_analysis',
#                         target_skill='general',
#                         priority='high'
#                     )
#                 )
#
#             logger.info(f"Generated {len(recommendations)} recommendations for {user.email}")
#             return recommendations
#
#         except Exception as e:
#             logger.error(f"Error generating recommendations: {str(e)}")
#             raise
#
#     @staticmethod
#     def get_user_recommendations(user, status='pending'):
#         """Foydalanuvchi tavsiyalarini olish"""
#         return Recommendation.objects.filter(
#             user=user,
#             status=status
#         ).order_by('-priority', '-created_at')
#
#     @staticmethod
#     def mark_recommendation_viewed(user, recommendation_id):
#         """Tavsiyani ko'rilgan deb belgilash"""
#         try:
#             recommendation = Recommendation.objects.get(
#                 id=recommendation_id,
#                 user=user
#             )
#             recommendation.status = 'viewed'
#             recommendation.viewed_at = timezone.now()
#             recommendation.save()
#
#             logger.info(f"Recommendation viewed: {user.email} -> {recommendation.id}")
#             return recommendation
#
#         except Recommendation.DoesNotExist:
#             raise ValueError("Tavsiya topilmadi")
#         except Exception as e:
#             logger.error(f"Error marking recommendation viewed: {str(e)}")
#             raise
#
#     @staticmethod
#     def complete_recommendation(user, recommendation_id):
#         """Tavsiyani bajarilgan deb belgilash"""
#         try:
#             recommendation = Recommendation.objects.get(
#                 id=recommendation_id,
#                 user=user
#             )
#             recommendation.status = 'completed'
#             recommendation.completed_at = timezone.now()
#             recommendation.save()
#
#             logger.info(f"Recommendation completed: {user.email} -> {recommendation.id}")
#             return recommendation
#
#         except Recommendation.DoesNotExist:
#             raise ValueError("Tavsiya topilmadi")
#         except Exception as e:
#             logger.error(f"Error completing recommendation: {str(e)}")
#             raise
#
#
# class DashboardService:
#     """Dashboard uchun service"""
#
#     @staticmethod
#     def get_dashboard_stats(user):
#         """Dashboard statistikasini olish"""
#         # Test sessiyalari
#         session_analytics = TestSessionService.get_session_analytics(user, days=30)
#
#         # Study sessiyalari
#         study_analytics = StudySessionService.get_study_analytics(user, days=30)
#
#         # Progress trackers
#         progress_trackers = ProgressTracker.objects.filter(user=user)
#
#         # Recommendations
#         recommendations_count = RecommendationService.get_user_recommendations(user).count()
#
#         # Recent activity
#         recent_sessions = TestSessionService.get_user_sessions(user, limit=5)
#
#         # Upcoming goals
#         upcoming_goals = progress_trackers.filter(
#             target_date__gte=timezone.now().date()
#         ).order_by('target_date')[:3]
#
#         return {
#             'overview': {
#                 'total_sessions': session_analytics['total_sessions'],
#                 'completed_sessions': session_analytics['completed_sessions'],
#                 'average_score': session_analytics['average_score'],
#                 'study_time_hours': study_analytics['total_time_spent'] / 60,
#                 'current_streak': sum(tracker.streak_days for tracker in progress_trackers),
#             },
#             'recent_activity': TestSessionSerializer(recent_sessions, many=True).data,
#             'upcoming_goals': [
#                 {
#                     'category': tracker.category.name,
#                     'target_band': tracker.target_band,
#                     'target_date': tracker.target_date,
#                     'days_remaining': (tracker.target_date - timezone.now().date()).days
#                 }
#                 for tracker in upcoming_goals
#             ],
#             'recommendations_count': recommendations_count,
#             'achievements': []  # Could be implemented with achievements system
#         }
