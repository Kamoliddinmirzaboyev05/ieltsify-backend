# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Avg, Count, Sum
# from django.urls import reverse
# from .models import (
#     TestSession, SectionAttempt, QuestionResponse, ProgressTracker,
#     StudySession, ErrorLog, Recommendation
# )
#
#
# @admin.register(TestSession)
# class TestSessionAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'title', 'session_type', 'status', 'started_at',
#                    'duration', 'total_score', 'overall_band')
#     list_filter = ('session_type', 'status', 'started_at')
#     search_fields = ('user__email', 'user__username', 'title', 'description')
#     ordering = ('-started_at',)
#     readonly_fields = ('uuid', 'started_at', 'completed_at', 'duration')
#
#     fieldsets = (
#         ('Session Information', {'fields': ('uuid', 'user', 'title', 'description')}),
#         ('Settings', {'fields': ('session_type',)}),
#         ('Timing', {'fields': ('started_at', 'completed_at', 'total_duration_minutes', 'duration')}),
#         ('Results', {'fields': ('total_score', 'total_percentage', 'overall_band')}),
#         ('Status', {'fields': ('status',)}),
#     )
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#     user_email.admin_order_field = 'user__email'
#
#     def duration(self, obj):
#         minutes = obj.get_duration_minutes()
#         if minutes > 0:
#             return f"{minutes} min"
#         return "Not completed"
#     duration.short_description = 'Duration'
#
#     def total_score(self, obj):
#         if obj.total_score:
#             if obj.total_score >= 7:
#                 return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', obj.total_score)
#             elif obj.total_score >= 6:
#                 return format_html('<span style="color: blue; font-weight: bold;">{:.1f}</span>', obj.total_score)
#             else:
#                 return format_html('<span style="color: orange;">{:.1f}</span>', obj.total_score)
#         return "N/A"
#     total_score.short_description = 'Score'
#
#     def overall_band(self, obj):
#         if obj.overall_band:
#             if obj.overall_band >= 7.0:
#                 return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.overall_band)
#             elif obj.overall_band >= 6.0:
#                 return format_html('<span style="color: blue; font-weight: bold;">{}</span>', obj.overall_band)
#             else:
#                 return format_html('<span style="color: orange;">{}</span>', obj.overall_band)
#         return "N/A"
#     overall_band.short_description = 'Band'
#
#     actions = ['complete_sessions', 'reset_sessions', 'generate_report']
#
#     def complete_sessions(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = 0
#         for session in queryset.filter(status='active'):
#             session.status = 'completed'
#             session.completed_at = timezone.now()
#             session.save()
#             count += 1
#
#         messages.success(request, f'{count} ta sessiya yakunlandi')
#     complete_sessions.short_description = 'Sessiyalarni yakunlash'
#
#     def reset_sessions(self, request, queryset):
#         from django.contrib import messages
#
#         count = queryset.update(status='active', completed_at=None, total_score=None)
#         messages.success(request, f'{count} ta sessiya qayta boshlandi')
#     reset_sessions.short_description = 'Sessiyalarni qayta boshlash'
#
#     def generate_report(self, request, queryset):
#         from django.contrib import messages
#         import csv
#         from django.http import HttpResponse
#
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="test_sessions_report.csv"'
#
#         writer = csv.writer(response)
#         writer.writerow(['User Email', 'Title', 'Type', 'Status', 'Started At', 'Duration (min)', 'Score', 'Band'])
#
#         for session in queryset:
#             writer.writerow([
#                 session.user.email,
#                 session.title,
#                 session.get_session_type_display(),
#                 session.get_status_display(),
#                 session.started_at.strftime('%Y-%m-%d %H:%M:%S'),
#                 session.get_duration_minutes(),
#                 session.total_score or '',
#                 session.overall_band or ''
#             ])
#
#         return response
#     generate_report.short_description = 'Hisobot yuklash'
#
#
# class QuestionResponseInline(admin.TabularInline):
#     model = QuestionResponse
#     extra = 0
#     readonly_fields = ('question', 'status', 'is_correct', 'points_earned', 'time_spent_seconds')
#     fields = ('question', 'status', 'is_correct', 'points_earned', 'time_spent_seconds')
#
#
# @admin.register(SectionAttempt)
# class SectionAttemptAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'section_type', 'test_title', 'started_at',
#                    'duration', 'score', 'band_score', 'accuracy')
#     list_filter = ('section_type', 'started_at')
#     search_fields = ('user__email', 'user__username', 'test__title')
#     ordering = ('-started_at',)
#     readonly_fields = ('started_at', 'completed_at', 'duration', 'accuracy')
#
#     fieldsets = (
#         ('Section Information', {'fields': ('session', 'user', 'section_type', 'test')}),
#         ('Timing', {'fields': ('started_at', 'completed_at', 'time_limit_minutes', 'duration')}),
#         ('Results', {'fields': ('score', 'percentage', 'band_score')}),
#         ('Statistics', {'fields': ('total_questions', 'correct_answers', 'skipped_questions', 'accuracy')}),
#         ('Payment', {'fields': ('coins_spent',)}),
#     )
#
#     inlines = [QuestionResponseInline]
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#     user_email.admin_order_field = 'user__email'
#
#     def test_title(self, obj):
#         return obj.test.title
#     test_title.short_description = 'Test'
#     test_title.admin_order_field = 'test__title'
#
#     def duration(self, obj):
#         minutes = obj.get_duration_minutes()
#         if minutes > 0:
#             return f"{minutes} min"
#         return "Not completed"
#     duration.short_description = 'Duration'
#
#     def accuracy(self, obj):
#         accuracy = obj.get_accuracy()
#         if accuracy > 80:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}%</span>', accuracy)
#         elif accuracy > 60:
#             return format_html('<span style="color: blue; font-weight: bold;">{:.1f}%</span>', accuracy)
#         else:
#             return format_html('<span style="color: orange;">{:.1f}%</span>', accuracy)
#     accuracy.short_description = 'Accuracy'
#
#     def score(self, obj):
#         if obj.score:
#             if obj.score >= 7:
#                 return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', obj.score)
#             elif obj.score >= 6:
#                 return format_html('<span style="color: blue; font-weight: bold;">{:.1f}</span>', obj.score)
#             else:
#                 return format_html('<span style="color: orange;">{:.1f}</span>', obj.score)
#         return "N/A"
#     score.short_description = 'Score'
#
#     def band_score(self, obj):
#         if obj.band_score:
#             if obj.band_score >= 7.0:
#                 return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.band_score)
#             elif obj.band_score >= 6.0:
#                 return format_html('<span style="color: blue; font-weight: bold;">{}</span>', obj.band_score)
#             else:
#                 return format_html('<span style="color: orange;">{}</span>', obj.band_score)
#         return "N/A"
#     band_score.short_description = 'Band'
#
#     actions = ['complete_sections', 'reset_sections', 'analyze_errors']
#
#     def complete_sections(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = 0
#         for section in queryset.filter(completed_at__isnull=True):
#             section.completed_at = timezone.now()
#             section.save()
#             count += 1
#
#         messages.success(request, f'{count} ta bo\'lim yakunlandi')
#     complete_sections.short_description = 'Bo\'limlarni yakunlash'
#
#     def reset_sections(self, request, queryset):
#         from django.contrib import messages
#
#         count = queryset.update(completed_at=None, score=None, percentage=None)
#         messages.success(request, f'{count} ta bo\'lim qayta boshlandi')
#     reset_sections.short_description = 'Bo\'limlarni qayta boshlash'
#
#     def analyze_errors(self, request, queryset):
#         from django.contrib import messages
#
#         # Xatoliklarni tahlil qilish logikasi
#         count = queryset.count()
#         messages.success(request, f'{count} ta bo\'lim uchun xatoliklar tahlil qilindi')
#     analyze_errors.short_description = 'Xatoliklarni tahlil qilish'
#
#
# @admin.register(QuestionResponse)
# class QuestionResponseAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'test_title', 'question_number', 'status',
#                    'time_spent', 'is_correct', 'points_earned')
#     list_filter = ('status', 'is_correct', 'answered_at')
#     search_fields = ('section_attempt__user__email', 'question__question_text')
#     ordering = ('-answered_at',)
#     readonly_fields = ('first_viewed_at', 'answered_at', 'time_spent_seconds')
#
#     def user_email(self, obj):
#         return obj.section_attempt.user.email
#     user_email.short_description = 'User'
#
#     def test_title(self, obj):
#         return obj.section_attempt.test.title
#     test_title.short_description = 'Test'
#
#     def question_number(self, obj):
#         return f"Q{obj.question.question_number}"
#     question_number.short_description = 'Question'
#
#     def time_spent(self, obj):
#         minutes = obj.time_spent_seconds // 60
#         seconds = obj.time_spent_seconds % 60
#         return f"{minutes}:{seconds:02d}"
#     time_spent.short_description = 'Time Spent'
#
#     def is_correct(self, obj):
#         if obj.is_correct is True:
#             return format_html('<span style="color: green; font-weight: bold;">✓</span>')
#         elif obj.is_correct is False:
#             return format_html('<span style="color: red; font-weight: bold;">✗</span>')
#         return format_html('<span style="color: gray;">-</span>')
#     is_correct.short_description = 'Correct'
#
#     def points_earned(self, obj):
#         if obj.points_earned > 0:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', obj.points_earned)
#         return "0.0"
#     points_earned.short_description = 'Points'
#
#     actions = ['mark_correct', 'mark_incorrect', 'reset_responses']
#
#     def mark_correct(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_correct=True, points_earned=1.0)
#         messages.success(request, f'{count} ta javob to\'g\'ri deb belgilandi')
#     mark_correct.short_description = 'To\'g\'ri deb belgilash'
#
#     def mark_incorrect(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_correct=False, points_earned=0)
#         messages.success(request, f'{count} ta javob noto\'g\'ri deb belgilandi')
#     mark_incorrect.short_description = 'Noto\'g\'ri deb belgilash'
#
#     def reset_responses(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_correct=None, points_earned=0)
#         messages.success(request, f'{count} ta javob qayta tiklandi')
#     reset_responses.short_description = 'Javoblarni qayta tiklash'
#
#
# @admin.register(ProgressTracker)
# class ProgressTrackerAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'category', 'total_tests', 'average_score', 'best_score',
#                    'current_band', 'progress_percentage', 'streak_days')
#     list_filter = ('category', 'streak_days')
#     search_fields = ('user__email', 'user__username')
#     ordering = ('-progress_percentage', 'user__email')
#     readonly_fields = ('created_at', 'updated_at')
#
#     fieldsets = (
#         ('User Information', {'fields': ('user', 'category')}),
#         ('Statistics', {'fields': ('total_tests_taken', 'total_time_spent_minutes', 'average_score', 'best_score')}),
#         ('Current Status', {'fields': ('current_band', 'progress_percentage', 'streak_days', 'last_activity_date')}),
#         ('Goals', {'fields': ('target_band', 'target_date')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#     user_email.admin_order_field = 'user__email'
#
#     def total_tests(self, obj):
#         return format_html('<span style="font-weight: bold;">{}</span>', obj.total_tests_taken)
#     total_tests.short_description = 'Tests'
#
#     def average_score(self, obj):
#         if obj.average_score > 0:
#             if obj.average_score >= 7:
#                 return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', obj.average_score)
#             elif obj.average_score >= 6:
#                 return format_html('<span style="color: blue; font-weight: bold;">{:.1f}</span>', obj.average_score)
#             else:
#                 return format_html('<span style="color: orange;">{:.1f}</span>', obj.average_score)
#         return "0.0"
#     average_score.short_description = 'Avg Score'
#
#     def best_score(self, obj):
#         if obj.best_score > 0:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', obj.best_score)
#         return "0.0"
#     best_score.short_description = 'Best Score'
#
#     def current_band(self, obj):
#         if obj.current_band > 0:
#             if obj.current_band >= 7.0:
#                 return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.current_band)
#             elif obj.current_band >= 6.0:
#                 return format_html('<span style="color: blue; font-weight: bold;">{}</span>', obj.current_band)
#             else:
#                 return format_html('<span style="color: orange;">{}</span>', obj.current_band)
#         return "0.0"
#     current_band.short_description = 'Current Band'
#
#     def progress_percentage(self, obj):
#         if obj.progress_percentage >= 80:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}%</span>', obj.progress_percentage)
#         elif obj.progress_percentage >= 50:
#             return format_html('<span style="color: blue; font-weight: bold;">{:.1f}%</span>', obj.progress_percentage)
#         else:
#             return format_html('<span style="color: orange;">{:.1f}%</span>', obj.progress_percentage)
#     progress_percentage.short_description = 'Progress'
#
#     def streak_days(self, obj):
#         if obj.streak_days >= 7:
#             return format_html('<span style="color: green; font-weight: bold;">{} days 🔥</span>', obj.streak_days)
#         elif obj.streak_days >= 3:
#             return format_html('<span style="color: blue; font-weight: bold;">{} days</span>', obj.streak_days)
#         else:
#             return f"{obj.streak_days} days"
#     streak_days.short_description = 'Streak'
#
#     actions = ['update_progress', 'reset_streak', 'set_target']
#
#     def update_progress(self, request, queryset):
#         from django.contrib import messages
#
#         count = 0
#         for tracker in queryset:
#             tracker.update_progress()
#             count += 1
#
#         messages.success(request, f'{count} ta progress yangilandi')
#     update_progress.short_description = 'Progressni yangilash'
#
#     def reset_streak(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(streak_days=0)
#         messages.success(request, f'{count} ta streak nolga qaytarildi')
#     reset_streak.short_description = 'Streakni nolga qaytarish'
#
#     def set_target(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(target_band=7.0)
#         messages.success(request, f'{count} ta foydalanuvchi uchun target 7.0 ga o\'rnatildi')
#     set_target.short_description = 'Targetni 7.0 ga o\'rnatish'
#
#
# @admin.register(StudySession)
# class StudySessionAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'material_title', 'session_type', 'started_at',
#                    'duration', 'completion', 'rating')
#     list_filter = ('session_type', 'rating', 'started_at')
#     search_fields = ('user__email', 'user__username', 'material__title')
#     ordering = ('-started_at',)
#     readonly_fields = ('started_at', 'duration')
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#
#     def material_title(self, obj):
#         return obj.material.title
#     material_title.short_description = 'Material'
#
#     def duration(self, obj):
#         if obj.duration_minutes > 0:
#             return f"{obj.duration_minutes} min"
#         return "Not completed"
#     duration.short_description = 'Duration'
#
#     def completion(self, obj):
#         if obj.completion_percentage >= 80:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}%</span>', obj.completion_percentage)
#         elif obj.completion_percentage >= 50:
#             return format_html('<span style="color: blue; font-weight: bold;">{:.1f}%</span>', obj.completion_percentage)
#         else:
#             return format_html('<span style="color: orange;">{:.1f}%</span>', obj.completion_percentage)
#     completion.short_description = 'Completion'
#
#     def rating(self, obj):
#         if obj.rating:
#             stars = '⭐' * obj.rating
#             return format_html('<span style="color: gold;">{}</span>', stars)
#         return "No rating"
#     rating.short_description = 'Rating'
#
#     actions = ['complete_sessions', 'reset_sessions', 'export_study_data']
#
#     def complete_sessions(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = 0
#         for session in queryset.filter(completed_at__isnull=True):
#             session.completed_at = timezone.now()
#             session.completion_percentage = 100
#             session.save()
#             count += 1
#
#         messages.success(request, f'{count} ta o\'qish sessiyasi yakunlandi')
#     complete_sessions.short_description = 'Sessiyalarni yakunlash'
#
#     def reset_sessions(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(completed_at=None, completion_percentage=0)
#         messages.success(request, f'{count} ta sessiya qayta boshlandi')
#     reset_sessions.short_description = 'Sessiyalarni qayta boshlash'
#
#     def export_study_data(self, request, queryset):
#         from django.contrib import messages
#         import csv
#         from django.http import HttpResponse
#
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="study_sessions_report.csv"'
#
#         writer = csv.writer(response)
#         writer.writerow(['User Email', 'Material', 'Type', 'Duration (min)', 'Completion (%)', 'Rating'])
#
#         for session in queryset:
#             writer.writerow([
#                 session.user.email,
#                 session.material.title,
#                 session.get_session_type_display(),
#                 session.duration_minutes,
#                 session.completion_percentage,
#                 session.rating or ''
#             ])
#
#         return response
#     export_study_data.short_description = 'O\'qish ma\'lumotlarini yuklash'
#
#
# @admin.register(ErrorLog)
# class ErrorLogAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'question_info', 'error_type', 'occurrence_count',
#                    'last_occurrence', 'status')
#     list_filter = ('error_type', 'status', 'last_occurrence')
#     search_fields = ('user__email', 'user__username', 'question__question_text', 'user_answer')
#     ordering = ('-last_occurrence',)
#     readonly_fields = ('first_occurrence', 'last_occurrence')
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#
#     def question_info(self, obj):
#         return f"Q{obj.question.question_number}: {obj.question.question_text[:30]}..."
#     question_info.short_description = 'Question'
#
#     def occurrence_count(self, obj):
#         if obj.occurrence_count > 5:
#             return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.occurrence_count)
#         elif obj.occurrence_count > 2:
#             return format_html('<span style="color: orange; font-weight: bold;">{}</span>', obj.occurrence_count)
#         return str(obj.occurrence_count)
#     occurrence_count.short_description = 'Count'
#
#     def status(self, obj):
#         if obj.status == 'resolved':
#             return format_html('<span style="color: green; font-weight: bold;">✓ Resolved</span>')
#         else:
#             return format_html('<span style="color: orange;">⚠ Pending</span>')
#     status.short_description = 'Status'
#
#     actions = ['resolve_errors', 'reset_errors', 'analyze_patterns']
#
#     def resolve_errors(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(status='resolved')
#         messages.success(request, f'{count} ta xatolik hal qilindi')
#     resolve_errors.short_description = 'Xatoliklarni hal qilish'
#
#     def reset_errors(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(status='pending')
#         messages.success(request, f'{count} ta xatolik qayta tiklandi')
#     reset_errors.short_description = 'Xatoliklarni qayta tiklash'
#
#     def analyze_patterns(self, request, queryset):
#         from django.contrib import messages
#         # Xatolik patternlarini tahlil qilish logikasi
#         count = queryset.count()
#         messages.success(request, f'{count} ta xatolik patternlari tahlil qilindi')
#     analyze_patterns.short_description = 'Patternlarni tahlil qilish'
#
#
# @admin.register(Recommendation)
# class RecommendationAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'title', 'recommendation_type', 'priority', 'status', 'created_at')
#     list_filter = ('recommendation_type', 'priority', 'status', 'created_at')
#     search_fields = ('user__email', 'user__username', 'title', 'description', 'target_skill')
#     ordering = ('-priority', '-created_at')
#     readonly_fields = ('created_at', 'viewed_at', 'completed_at')
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'User'
#
#     def priority(self, obj):
#         if obj.priority == 'high':
#             return format_html('<span style="color: red; font-weight: bold;">HIGH</span>')
#         elif obj.priority == 'medium':
#             return format_html('<span style="color: orange; font-weight: bold;">MEDIUM</span>')
#         else:
#             return format_html('<span style="color: blue;">LOW</span>')
#     priority.short_description = 'Priority'
#
#     def status(self, obj):
#         if obj.status == 'completed':
#             return format_html('<span style="color: green; font-weight: bold;">✓ Completed</span>')
#         elif obj.status == 'viewed':
#             return format_html('<span style="color: blue;">👁 Viewed</span>')
#         elif obj.status == 'dismissed':
#             return format_html('<span style="color: gray;">✗ Dismissed</span>')
#         else:
#             return format_html('<span style="color: orange;">⏳ Pending</span>')
#     status.short_description = 'Status'
#
#     actions = ['mark_viewed', 'mark_completed', 'dismiss_recommendations', 'generate_personalized']
#
#     def mark_viewed(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = queryset.filter(status='pending').update(
#             status='viewed',
#             viewed_at=timezone.now()
#         )
#         messages.success(request, f'{count} ta tavsiya ko\'rilgan deb belgilandi')
#     mark_viewed.short_description = 'Ko\'rilgan deb belgilash'
#
#     def mark_completed(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = queryset.filter(status__in=['pending', 'viewed']).update(
#             status='completed',
#             completed_at=timezone.now()
#         )
#         messages.success(request, f'{count} ta tavsiya bajarilgan deb belgilandi')
#     mark_completed.short_description = 'Bajarilgan deb belgilash'
#
#     def dismiss_recommendations(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(status='dismissed')
#         messages.success(request, f'{count} ta tavsiya rad etildi')
#     dismiss_recommendations.short_description = 'Rad etish'
#
#     def generate_personalized(self, request, queryset):
#         from django.contrib import messages
#         # Personalized tavsiyalarni generatsiya qilish logikasi
#         count = queryset.count()
#         messages.success(request, f'{count} ta foydalanuvchi uchun personalized tavsiyalar yaratildi')
#     generate_personalized.short_description = 'Personalized tavsiyalar yaratish'
