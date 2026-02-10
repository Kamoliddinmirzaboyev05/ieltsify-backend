# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Avg, Count, Sum
# from django.urls import reverse
# from django.utils.safestring import mark_safe
# from .models import (
#     TestCategory, Test, Question, AnswerOption, MatchingItem,
#     TestAttempt, UserAnswer, TestResult, StudyMaterial
# )
#
#
# @admin.register(TestCategory)
# class TestCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'icon', 'is_active', 'order', 'test_count')
#     list_filter = ('is_active', 'name')
#     search_fields = ('name', 'description')
#     ordering = ('order', 'name')
#     readonly_fields = ('created_at', 'updated_at')
#
#     fieldsets = (
#         ('Category Information', {'fields': ('name', 'description', 'icon')}),
#         ('Settings', {'fields': ('is_active', 'order')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def test_count(self, obj):
#         count = obj.tests.count()
#         url = reverse('admin:modules_test_changelist') + f'?category__id__exact={obj.id}'
#         return format_html('<a href="{}">{} tests</a>', url, count)
#     test_count.short_description = 'Tests'
#     test_count.admin_order_field = 'tests__count'
#
#
# class AnswerOptionInline(admin.TabularInline):
#     model = AnswerOption
#     extra = 4
#     fields = ('option_label', 'option_text', 'is_correct', 'order')
#     ordering = ('order',)
#
#
# class MatchingItemInline(admin.TabularInline):
#     model = MatchingItem
#     extra = 2
#     fields = ('left_item', 'right_item', 'is_correct_pair', 'pair_order')
#     ordering = ('pair_order',)
#
#
# @admin.register(Test)
# class TestAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'test_type', 'difficulty', 'duration_minutes',
#                    'coin_cost', 'is_free', 'is_published', 'average_score', 'total_attempts')
#     list_filter = ('category', 'test_type', 'difficulty', 'is_free', 'is_published')
#     search_fields = ('title', 'description')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'updated_at', 'average_score', 'total_attempts')
#
#     fieldsets = (
#         ('Basic Information', {'fields': ('title', 'description', 'category')}),
#         ('Test Settings', {'fields': ('test_type', 'difficulty', 'duration_minutes', 'total_questions')}),
#         ('Scoring', {'fields': ('max_score',)}),
#         ('Pricing', {'fields': ('coin_cost', 'is_free')}),
#         ('Status', {'fields': ('is_active', 'is_published')}),
#         ('Creator', {'fields': ('created_by',)}),
#         ('Statistics', {'fields': ('average_score', 'total_attempts')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def average_score(self, obj):
#         score = obj.get_average_score()
#         if score > 7:
#             return format_html('<span style="color: green; font-weight: bold;">{:.1f}</span>', score)
#         elif score > 5:
#             return format_html('<span style="color: orange; font-weight: bold;">{:.1f}</span>', score)
#         else:
#             return format_html('<span style="color: red;">{:.1f}</span>', score)
#     average_score.short_description = 'Avg Score'
#
#     def total_attempts(self, obj):
#         count = obj.get_total_attempts()
#         return format_html('<span style="font-weight: bold;">{}</span>', count)
#     total_attempts.short_description = 'Attempts'
#
#     actions = ['publish_selected', 'unpublish_selected', 'make_free', 'make_paid']
#
#     def publish_selected(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_published=True)
#         messages.success(request, f'{count} ta test nashr qilindi')
#     publish_selected.short_description = 'Tanlangan testlarni nashr qilish'
#
#     def unpublish_selected(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_published=False)
#         messages.success(request, f'{count} ta test nashrdan olindi')
#     unpublish_selected.short_description = 'Tanlangan testlarni nashrdan olish'
#
#     def make_free(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_free=True, coin_cost=0)
#         messages.success(request, f'{count} ta test bepul qilindi')
#     make_free.short_description = 'Bepul qilish'
#
#     def make_paid(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_free=False, coin_cost=10)
#         messages.success(request, f'{count} ta test pullik qilindi')
#     make_paid.short_description = 'Pullik qilish'
#
#
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('test_info', 'question_number', 'question_type', 'section',
#                    'points', 'is_mandatory', 'question_preview')
#     list_filter = ('question_type', 'test__category', 'test__difficulty', 'section')
#     search_fields = ('question_text', 'test__title')
#     ordering = ('test', 'question_number')
#     readonly_fields = ('created_at', 'updated_at')
#
#     fieldsets = (
#         ('Question Information', {'fields': ('test', 'question_number', 'section')}),
#         ('Content', {'fields': ('question_text', 'question_image', 'question_audio')}),
#         ('Settings', {'fields': ('question_type', 'points', 'is_mandatory')}),
#         ('Help', {'fields': ('hint', 'explanation')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     inlines = [AnswerOptionInline, MatchingItemInline]
#
#     def test_info(self, obj):
#         return f"{obj.test.title} ({obj.test.get_category_display()})"
#     test_info.short_description = 'Test'
#     test_info.admin_order_field = 'test__title'
#
#     def question_preview(self, obj):
#         preview = obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
#         return format_html('<span title="{}">{}</span>', obj.question_text, preview)
#     question_preview.short_description = 'Question Preview'
#
#     actions = ['duplicate_questions', 'bulk_points_update']
#
#     def duplicate_questions(self, request, queryset):
#         from django.contrib import messages
#
#         count = 0
#         for question in queryset:
#             # Asl savolni nusxalash
#             question.pk = None
#             question.question_number += 1000  # Vaqtincha raqamni o'zgartirish
#             question.save()
#             count += 1
#
#         messages.success(request, f'{count} ta savol nusxalandi')
#     duplicate_questions.short_description = 'Savollarni nusxalash'
#
#     def bulk_points_update(self, request, queryset):
#         from django.contrib import messages
#
#         count = queryset.update(points=1.0)
#         messages.success(request, f'{count} ta savolning balli 1.0 ga yangilandi')
#     bulk_points_update.short_description = 'Ballarni 1.0 ga yangilash'
#
#
# @admin.register(AnswerOption)
# class AnswerOptionAdmin(admin.ModelAdmin):
#     list_display = ('question_info', 'option_label', 'option_preview', 'is_correct', 'order')
#     list_filter = ('is_correct', 'question__question_type')
#     search_fields = ('option_text', 'question__question_text')
#     ordering = ('question', 'order')
#
#     def question_info(self, obj):
#         return f"Q{obj.question.question_number}: {obj.question.test.title}"
#     question_info.short_description = 'Question'
#
#     def option_preview(self, obj):
#         preview = obj.option_text[:30] + "..." if len(obj.option_text) > 30 else obj.option_text
#         color = 'green' if obj.is_correct else 'black'
#         return format_html('<span style="color: {};">{}</span>', color, preview)
#     option_preview.short_description = 'Option'
#
#     actions = ['mark_correct', 'mark_incorrect', 'randomize_order']
#
#     def mark_correct(self, request, queryset):
#         from django.contrib import messages
#
#         # Avval barcha variantlarni noto'g'ri qilish
#         for option in queryset:
#             option.question.answer_options.all().update(is_correct=False)
#
#         # Tanlanganlarni to'g'ri qilish
#         count = queryset.update(is_correct=True)
#         messages.success(request, f'{count} ta variant to\'g\'ri deb belgilandi')
#     mark_correct.short_description = 'To\'g\'ri deb belgilash'
#
#     def mark_incorrect(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_correct=False)
#         messages.success(request, f'{count} ta variant noto\'g\'ri deb belgilandi')
#     mark_incorrect.short_description = 'Noto\'g\'ri deb belgilash'
#
#     def randomize_order(self, request, queryset):
#         from django.contrib import messages
#         import random
#
#         for option in queryset:
#             option.order = random.randint(1, 100)
#             option.save()
#
#         messages.success(request, f'{queryset.count()} ta variantning tartibi o\'zgartirildi')
#     randomize_order.short_description = 'Tartibni aralashtirish'
#
#
# @admin.register(MatchingItem)
# class MatchingItemAdmin(admin.ModelAdmin):
#     list_display = ('question_info', 'left_item_preview', 'right_item_preview', 'is_correct_pair', 'pair_order')
#     list_filter = ('is_correct_pair', 'question__question_type')
#     search_fields = ('left_item', 'right_item', 'question__question_text')
#     ordering = ('question', 'pair_order')
#
#     def question_info(self, obj):
#         return f"Q{obj.question.question_number}: {obj.question.test.title}"
#     question_info.short_description = 'Question'
#
#     def left_item_preview(self, obj):
#         preview = obj.left_item[:20] + "..." if len(obj.left_item) > 20 else obj.left_item
#         return preview
#     left_item_preview.short_description = 'Left Item'
#
#     def right_item_preview(self, obj):
#         preview = obj.right_item[:20] + "..." if len(obj.right_item) > 20 else obj.right_item
#         return preview
#     right_item_preview.short_description = 'Right Item'
#
#
# class UserAnswerInline(admin.TabularInline):
#     model = UserAnswer
#     extra = 0
#     readonly_fields = ('question', 'selected_option', 'text_answer', 'is_correct', 'points_earned')
#     fields = ('question', 'selected_option', 'text_answer', 'is_correct', 'points_earned')
#
#
# @admin.register(TestAttempt)
# class TestAttemptAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'test_title', 'status', 'started_at', 'duration',
#                    'score', 'percentage', 'coins_spent')
#     list_filter = ('status', 'test__category', 'started_at')
#     search_fields = ('user__email', 'user__username', 'test__title')
#     ordering = ('-started_at',)
#     readonly_fields = ('uuid', 'started_at', 'completed_at', 'duration', 'time_remaining')
#
#     fieldsets = (
#         ('Attempt Information', {'fields': ('uuid', 'user', 'test')}),
#         ('Status', {'fields': ('status',)}),
#         ('Timing', {'fields': ('started_at', 'completed_at', 'time_limit_minutes', 'duration', 'time_remaining')}),
#         ('Results', {'fields': ('score', 'percentage', 'correct_answers', 'total_answered')}),
#         ('Payment', {'fields': ('coins_spent',)}),
#     )
#
#     inlines = [UserAnswerInline]
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
#     def time_remaining(self, obj):
#         minutes = obj.get_time_remaining_minutes()
#         if minutes > 10:
#             return format_html('<span style="color: green;">{} min</span>', minutes)
#         elif minutes > 0:
#             return format_html('<span style="color: orange;">{} min</span>', minutes)
#         else:
#             return format_html('<span style="color: red;">Expired</span>')
#     time_remaining.short_description = 'Time Remaining'
#
#     actions = ['complete_attempts', 'reset_attempts', 'refund_coins']
#
#     def complete_attempts(self, request, queryset):
#         from django.contrib import messages
#         from django.utils import timezone
#
#         count = 0
#         for attempt in queryset.filter(status='in_progress'):
#             attempt.status = 'completed'
#             attempt.completed_at = timezone.now()
#             attempt.save()
#             count += 1
#
#         messages.success(request, f'{count} ta test yakunlandi')
#     complete_attempts.short_description = 'Testlarni yakunlash'
#
#     def reset_attempts(self, request, queryset):
#         from django.contrib import messages
#
#         count = queryset.update(status='in_progress', completed_at=None, score=None, percentage=None)
#         messages.success(request, f'{count} ta test qayta boshlandi')
#     reset_attempts.short_description = 'Testlarni qayta boshlash'
#
#     def refund_coins(self, request, queryset):
#         from django.contrib import messages
#         from accounts.models import CoinTransaction, UserProfile
#
#         count = 0
#         for attempt in queryset:
#             if attempt.coins_spent > 0:
#                 # Coinlarni qaytarish
#                 profile = attempt.user.profile
#                 profile.coins += attempt.coins_spent
#                 profile.save()
#
#                 # Transaction yaratish
#                 CoinTransaction.objects.create(
#                     user=attempt.user,
#                     amount=attempt.coins_spent,
#                     type='in',
#                     reason='admin_adjustment',
#                     description=f'Refund for test: {attempt.test.title}'
#                 )
#
#                 count += 1
#
#         messages.success(request, f'{count} ta foydalanuvchiga coinlar qaytarildi')
#     refund_coins.short_description = 'Coinlarni qaytarish'
#
#
# @admin.register(TestResult)
# class TestResultAdmin(admin.ModelAdmin):
#     list_display = ('user_email', 'test_title', 'overall_band', 'listening_band',
#                    'reading_band', 'writing_band', 'speaking_band', 'percentile')
#     list_filter = ('overall_band',)
#     search_fields = ('attempt__user__email', 'attempt__test__title')
#     ordering = ('-attempt__started_at',)
#     readonly_fields = ('attempt', 'created_at', 'updated_at')
#
#     fieldsets = (
#         ('Test Information', {'fields': ('attempt',)}),
#         ('IELTS Bands', {'fields': ('listening_band', 'reading_band', 'writing_band', 'speaking_band', 'overall_band')}),
#         ('Scores', {'fields': ('listening_score', 'reading_score', 'writing_score', 'speaking_score')}),
#         ('Analysis', {'fields': ('strengths', 'weaknesses', 'recommendations')}),
#         ('Statistics', {'fields': ('percentile', 'rank', 'total_participants')}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     def user_email(self, obj):
#         return obj.attempt.user.email
#     user_email.short_description = 'User'
#
#     def test_title(self, obj):
#         return obj.attempt.test.title
#     test_title.short_description = 'Test'
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
#     overall_band.short_description = 'Overall Band'
#     overall_band.admin_order_field = 'overall_band'
#
#
# @admin.register(StudyMaterial)
# class StudyMaterialAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'material_type', 'coin_cost', 'is_free',
#                    'download_count', 'view_count', 'is_active')
#     list_filter = ('category', 'material_type', 'is_free', 'is_active')
#     search_fields = ('title', 'description')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'updated_at')
#
#     fieldsets = (
#         ('Material Information', {'fields': ('title', 'description', 'category')}),
#         ('Content', {'fields': ('material_type', 'file', 'url')}),
#         ('Pricing', {'fields': ('coin_cost', 'is_free')}),
#         ('Statistics', {'fields': ('download_count', 'view_count')}),
#         ('Status', {'fields': ('is_active',)}),
#         ('Timestamps', {'fields': ('created_at', 'updated_at')}),
#     )
#
#     actions = ['make_free_materials', 'make_paid_materials', 'reset_stats']
#
#     def make_free_materials(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_free=True, coin_cost=0)
#         messages.success(request, f'{count} ta material bepul qilindi')
#     make_free_materials.short_description = 'Bepul qilish'
#
#     def make_paid_materials(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(is_free=False, coin_cost=5)
#         messages.success(request, f'{count} ta material pullik qilindi')
#     make_paid_materials.short_description = 'Pullik qilish'
#
#     def reset_stats(self, request, queryset):
#         from django.contrib import messages
#         count = queryset.update(download_count=0, view_count=0)
#         messages.success(request, f'{count} ta material statistikasi nolga qaytarildi')
#     reset_stats.short_description = 'Statistikani nolga qaytarish'
